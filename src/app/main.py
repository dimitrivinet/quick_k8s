from fastapi import FastAPI

from app import pre_init, routers

pre_init.pre_init()

app = FastAPI()

app.include_router(routers.router)


@app.get("/")
async def home():

    return {"msg": "Welcome to the quick_k8s API. More info @ /docs"}
