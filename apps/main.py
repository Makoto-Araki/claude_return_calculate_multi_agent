from fastapi import FastAPI

from apps.routers.add import router as add_router

app = FastAPI(title="calculator-api")

app.include_router(add_router)
