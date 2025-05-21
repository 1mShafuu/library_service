import json
from datetime import date
from typing import List
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Loan, Reader, Address


#TODO : допилить нужные отчеты, пока только геометки есть

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