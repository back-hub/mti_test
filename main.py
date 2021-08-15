from fastapi import FastAPI
from blog import models, routers
from core.db import engine
from blog import routers


models.Base.metadata.create_all(bind=engine)


fastapp = FastAPI()

fastapp.include_router(routers.router)
