from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.tasks.celery import generate_report_task
from app.db.session import get_db

router = APIRouter(tags=["reports"])


@router.post("/geojson")
async def trigger_geojson_report():
    task = generate_report_task.delay()
    return {"task_id": task.id}


@router.get("/geojson/{task_id}")
async def get_geojson_report(task_id: str):
    try:
        return FileResponse(f"reports/geojson_{task_id}.geojson")
    except FileNotFoundError:
        return {"status": "Report not ready yet"}
