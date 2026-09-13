from fastapi import FastAPI

from apps.routers.add import router as add_router
from apps.routers.subtract import router as subtract_router

app = FastAPI(title="calculator-api")

app.include_router(add_router)
app.include_router(subtract_router)
