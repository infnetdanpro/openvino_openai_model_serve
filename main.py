import uvicorn

from config import config
from server.app import create_app

app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host=config.HTTP_HOST, port=config.HTTP_PORT)
