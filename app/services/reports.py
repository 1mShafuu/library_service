import json
from datetime import date
from typing import List
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Loan, Reader, Address, Book, Author


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.geolocator = Nominatim(
            user_agent=settings.PROJECT_NAME,
            timeout=settings.GEOCODING_TIMEOUT
        )

    async def generate_geojson(self) -> str:
        result = await self.db.execute(
            select(Address)
            .join(Reader)
            .join(Loan)
            .where(Loan.return_date.is_(None))
        )

        features = []
        addresses = result.scalars().all()

        for address in addresses:
            try:
                location = self.geolocator.geocode(
                    f"{address.street}, {address.city}",
                    timeout=10
                )
                if location:
                    features.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [location.longitude, location.latitude]
                        },
                        "properties": {
                            "city": address.city,
                            "street": address.street
                        }
                    })
            except GeocoderTimedOut:
                continue

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        filename = f"reports/geojson_{date.today().isoformat()}.geojson"
        with open(filename, "w") as f:
            json.dump(geojson, f)

        return filename

    async def count_books_and_readers(self) -> dict:
        books_count = await self.db.scalar(select(func.count(Book.id)))
        readers_count = await self.db.scalar(select(func.count(Reader.id)))
        return {"total_books": books_count, "total_readers": readers_count}

    async def books_taken_by_readers(self) -> List[dict]:
        result = await self.db.execute(
            select(Reader.id, Reader.name, func.count(Loan.id))
            .join(Loan, Loan.reader_id == Reader.id)
            .group_by(Reader.id)
        )
        return [{"reader_id": row[0], "name": row[1], "total_books_taken": row[2]} for row in result.all()]

    async def books_currently_held_by_readers(self) -> List[dict]:
        result = await self.db.execute(
            select(Reader.id, Reader.name, func.count(Loan.id))
            .join(Loan, Loan.reader_id == Reader.id)
            .where(Loan.return_date.is_(None))
            .group_by(Reader.id)
        )
        return [{"reader_id": row[0], "name": row[1], "books_on_hand": row[2]} for row in result.all()]

    async def last_visit_dates(self) -> List[dict]:
        result = await self.db.execute(
            select(Reader.id, Reader.name, func.max(Loan.loan_date))
            .join(Loan, Loan.reader_id == Reader.id)
            .group_by(Reader.id)
        )
        return [{"reader_id": row[0], "name": row[1], "last_visit": row[2]} for row in result.all()]

    async def most_read_author(self) -> dict:
        result = await self.db.execute(
            select(Author.name, func.count(Loan.id).label("loan_count"))
            .join(Book, Book.author_id == Author.id)
            .join(Loan, Loan.book_id == Book.id)
            .group_by(Author.name)
            .order_by(desc("loan_count"))
            .limit(1)
        )
        row = result.first()
        return {"author": row[0], "loan_count": row[1]} if row else {}

    async def popular_genres(self) -> List[dict]:
        result = await self.db.execute(
            select(Book.genre, func.count(Loan.id))
            .join(Loan, Loan.book_id == Book.id)
            .group_by(Book.genre)
            .order_by(desc(func.count(Loan.id)))
        )
        return [{"genre": row[0], "loan_count": row[1]} for row in result.all()]

    async def favorite_genre_per_reader(self) -> List[dict]:
        # Предварительно
        subquery = (
            select(
                Reader.id.label("reader_id"),
                Book.genre,
                func.count(Loan.id).label("genre_count")
            )
            .join(Loan, Loan.reader_id == Reader.id)
            .join(Book, Loan.book_id == Book.id)
            .group_by(Reader.id, Book.genre)
            .subquery()
        )

        # Подзапрос с максимальным количеством для каждого читателя
        max_counts = (
            select(
                subquery.c.reader_id,
                func.max(subquery.c.genre_count).label("max_count")
            )
            .group_by(subquery.c.reader_id)
            .subquery()
        )

        # Финальный запрос
        result = await self.db.execute(
            select(
                subquery.c.reader_id,
                subquery.c.genre,
                subquery.c.genre_count
            ).join(
                max_counts,
                onclause=and_(
                    subquery.c.reader_id == max_counts.c.reader_id,
                    subquery.c.genre_count == max_counts.c.max_count
                )
            )
        )

        return [{"reader_id": row[0], "favorite_genre": row[1], "times_read": row[2]} for row in result.all()]