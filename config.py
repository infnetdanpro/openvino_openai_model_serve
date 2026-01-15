from openvino_genai import LLMPipeline, VLMPipeline
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    HTTP_HOST: str = "0.0.0.0"
    HTTP_PORT: int = 11434

    DEVICE: str = "CPU"  # e.g., "CPU", "NPU", "GPU.0"

    MODELS_DIR: str = "models"
    # {"model_id": (model_name, pipeline_class)}
    MODELS: dict = {
        "gemma": ("gemma-3-4b-it-int4-cw-ov", VLMPipeline),
        "mistral": ("mistral-7b-instruct-v0.1-int4-ov", LLMPipeline),
    }

    model_config = SettingsConfigDict(env_file=".env")


config = Config()
