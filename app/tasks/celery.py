from celery import Celery
from app.core.config import settings
from app.services.reports import ReportService
from app.db.session import SessionLocal

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND

@celery.task
def generate_report_task():
    with SessionLocal() as db:
        service = ReportService(db)
        filename = service.generate_geojson()
    return filename