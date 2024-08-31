from fastapi import FastAPI

from co_table import config

from contextlib import asynccontextmanager

from . import models
from . import routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if models.engine is not None:
        await models.close_session()
        await models.engine.dispose()

def create_app(settings = None):
    if not settings:
        settings = config.get_setting()

    app = FastAPI(lifespan = lifespan)

    models.init_db(settings)

    routers.init_routers(app)

    return app