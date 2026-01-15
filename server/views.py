import asyncio
import os
import queue
import threading
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import openvino_genai
import orjson as json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from config import config
from llm_pool import PipelinePool
from server.models import ChatRequest

router = APIRouter()


pools: dict[str, "PipelinePool"] = {}

for model_id, model_cfg in config.MODELS.items():
    model_name, genai_cls = model_cfg
    pools[model_name] = PipelinePool(
        genai_cls,
        model_path=os.path.join(config.MODELS_DIR, model_name),
        device=config.DEVICE,
        size=1,
    )


def build_prompt(messages):
    text = ""
    for m in messages:
        text += f"{m.role}: {m.content}\n"
    return text


@router.get("/models")
async def get_models():
    result = []
    for _, model_cfg in config.MODELS.items():
        result.append({"id": model_cfg[0], "object": "model"})
    return {"data": result}


@router.post("/chat/completions")
async def create_chat_completion(chat_request: ChatRequest):
    if chat_request.model not in pools:
        raise HTTPException(status_code=404, detail="Model not found")

    pool = pools[chat_request.model]
    pipe = pool.acquire()
    prompt = build_prompt(chat_request.messages)

    base_config = openvino_genai.GenerationConfig(
        temperature=chat_request.temperature,
        # max_new_tokens=2048,
        top_p=0.95,
        top_k=60,
    )

    if chat_request.stream:

        def generate():
            output_queue = queue.Queue()

            def streamer(token: str):
                output_queue.put(token)
                return False

            def worker():
                try:
                    pipe.start_chat()
                    pipe.generate(
                        prompt, generation_config=base_config, streamer=streamer
                    )
                finally:
                    output_queue.put(None)
                    pool.release(pipe)

            threading.Thread(target=worker).start()

            while True:
                token = output_queue.get()
                if token is None:
                    break
                chunk = {
                    "id": f"chatcmpl-{uuid.uuid4().hex}",
                    "object": "chat.completion.chunk",
                    "created": int(datetime.utcnow().timestamp()),
                    "model": chat_request.model,
                    "choices": [
                        {"delta": {"content": token}, "index": 0, "finish_reason": None}
                    ],
                }
                yield f"data: {json.dumps(chunk).decode()}\n\n"

            # Завершающий chunk с finish_reason="stop"
            final_chunk = {
                "id": f"chatcmpl-{uuid.uuid4().hex}",
                "object": "chat.completion.chunk",
                "created": int(datetime.utcnow().timestamp()),
                "model": chat_request.model,
                "choices": [{"delta": {}, "index": 0, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(final_chunk).decode()}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    # Blocked working mode
    output_queue = queue.Queue()

    def generate_non_stream():
        output = ""

        def streamer(token: str):
            nonlocal output
            output += token
            return False

        try:
            pipe.start_chat()
            pipe.generate(prompt, generation_config=base_config, streamer=streamer)
        finally:
            output_queue.put(output)
            pool.release(pipe)

    # Запускаем генерацию в отдельном потоке
    threading.Thread(target=generate_non_stream).start()

    # Ждем результат без блокировки FastAPI event loop
    output = await asyncio.to_thread(output_queue.get)

    result = {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "created": int(datetime.utcnow().timestamp()),
        "object": "chat.completion",
        "model": chat_request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": output},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },  # TODO: calculate tokens
    }
    return result
