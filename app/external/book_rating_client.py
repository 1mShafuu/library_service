import aiohttp
from typing import Optional
from app.core.config import settings


class BookRatingClient:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    API_KEY = settings.GOOGLE_BOOKS_API_KEY

    async def get_rating(self, title: str) -> Optional[float]:
        url = f"{self.BASE_URL}?q={title}&key={self.API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items")
                    if items:
                        volume_info = items[0].get("volumeInfo", {})
                        return volume_info.get("averageRating")
        return None
