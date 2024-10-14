from fastapi import FastAPI

from co_table import config

from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

from . import models
from . import routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    await models.create_all()
    yield
    if models.engine is not None:
        await models.close_session()
        await models.engine.dispose()

def create_app(settings = None):
    
    if not settings:
        settings = config.get_setting()
    
    app = FastAPI(lifespan = lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[""],
        allow_credentials=True,
        allow_methods=[""],
        allow_headers=["*"],
    )

    models.init_db(settings)

    routers.init_routers(app)

    return app