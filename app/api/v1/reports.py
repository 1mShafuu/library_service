from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.tasks.celery import generate_report_task
from app.db.session import get_db
from app.services.reports import ReportService

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

@router.get("/summary")
async def summary(db: AsyncSession = Depends(get_db)):
    return await ReportService(db).count_books_and_readers()

@router.get("/books-by-readers")
async def books_by_readers(db: AsyncSession = Depends(get_db)):
    return await ReportService(db).books_taken_by_readers()

@router.get("/books-on-hands")
async def books_on_hands(db: AsyncSession = Depends(get_db)):
    return await ReportService(db).books_currently_held_by_readers()

@router.get("/last-visits")
async def last_visits(db: AsyncSession = Depends(get_db)):
    return await ReportService(db).last_visit_dates()

@router.get("/top-author")
async def top_author(db: AsyncSession = Depends(get_db)):
    return await ReportService(db).most_read_author()

@router.get("/popular-genres")
async def popular_genres(db: AsyncSession = Depends(get_db)):
    return await ReportService(db).popular_genres()

@router.get("/favorite-genres")
async def favorite_genres(db: AsyncSession = Depends(get_db)):
    return await ReportService(db).favorite_genre_per_reader()