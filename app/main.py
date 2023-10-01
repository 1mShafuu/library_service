from contextlib import asynccontextmanager
import asyncio
print("Task is from:", asyncio.Task.__module__)
print("Task:", asyncio.Task)
from fastapi import FastAPI
from app.db.session import engine, Base
from app.api.v1 import books_router, readers_router, loans_router, reports_router
import uvicorn
from app import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы")
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(books_router, prefix="/api/v1/books")
app.include_router(readers_router, prefix="/api/v1/readers")
app.include_router(loans_router, prefix="/api/v1/loans")
app.include_router(reports_router, prefix="/api/v1/reports")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
