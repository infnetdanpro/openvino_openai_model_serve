from queue import Queue


class PipelinePool:
    def __init__(self, genai_cls, model_path: str, device="CPU", size=1):
        self.q = Queue()
        for _ in range(size):
            pipeline = genai_cls(model_path, device)
            self.q.put(pipeline)

    def acquire(self):
        return self.q.get()

    def release(self, pipeline):
        self.q.put(pipeline)
