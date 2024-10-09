import os
import json
from datetime import date
import pandas as pd
import ssl
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from urllib.request import urlopen

class Reports:
    def __init__(self, db):
        self.db = db
        self.report_dir = "reports/"
        
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data)
        df.to_csv(f"{self.report_dir}{filename}.csv", index=False)

    # Отчет: книги, взятые каждым читателем
    def report_reader_history(self):
        history = self.db.fetch_query('''
            SELECT r.name AS reader_name, COUNT(bl.book_id) AS taken_books
            FROM book_loans bl
            LEFT JOIN readers r ON r.id = bl.reader_id
            GROUP BY r.id
            ORDER BY r.name;
        ''')
        self.save_to_csv(history, "reader_history")

        for name, count in history:
            print(f"Reader: {name}, Books borrowed: {count}")

    # Отчет: книги, которые на данный момент на руках у читателей
    def report_current_loans(self):
        loans = self.db.fetch_query('''
            SELECT r.name AS reader_name, COUNT(bl.book_id) AS taken_books
            FROM book_loans bl
            LEFT JOIN readers r ON r.id = bl.reader_id
            WHERE bl.return_date IS NULL
            GROUP BY r.id
            ORDER BY r.name;
        ''')
        self.save_to_csv(loans, "current_loans")

        for name, count in loans:
            print(f"Reader: {name}, Books currently borrowed: {count}")

    # Отчет: дата последнего визита каждого читателя
    def report_last_visit(self):
        visits = self.db.fetch_query('''
            SELECT reader_name, last_visit_date
            FROM (
                SELECT reader_name, last_visit_date, ROW_NUMBER() OVER (PARTITION BY reader_name ORDER BY last_visit_date DESC) AS rn
                FROM (
                    SELECT 
                        r.name AS reader_name,
                        CASE
                            WHEN bl.return_date IS NULL THEN bl.loan_date
                            ELSE bl.return_date
                        END AS last_visit_date
                    FROM book_loans bl
                    LEFT JOIN readers r ON r.id = bl.reader_id
                ) res
            ) res2
            WHERE rn = 1;
        ''')
        self.save_to_csv(visits, "last_visit")

        for name, last_visit in visits:
            print(f"Reader: {name}, Last visit: {last_visit}")

    # Отчет: любимый жанр конкретного читателя
    def report_favorite_genre_by_reader(self):
        favorite_genres = self.db.fetch_query('''
            SELECT reader_name, favorite_genre
            FROM (
                SELECT r.name AS reader_name,
                       b.genre AS favorite_genre,
                       COUNT(bl.book_id) AS genre_count,
                       ROW_NUMBER() OVER (PARTITION BY r.id ORDER BY COUNT(bl.book_id) DESC) AS rn
                FROM book_loans bl
                LEFT JOIN readers r ON r.id = bl.reader_id
                LEFT JOIN books b ON b.id = bl.book_id
                GROUP BY r.id, b.genre
            ) AS subquery
            WHERE rn = 1
            ORDER BY reader_name;
        ''')
        
        self.save_to_csv(favorite_genres, "favorite_genre_by_reader")
        
        for reader, genre in favorite_genres:
            print(f"Reader: {reader}, Favorite genre: {genre}")

    # Отчет: просроченные книги
    def report_overdue_books(self):
        overdue_books = self.db.fetch_query('''
            SELECT b.title, r.name AS reader_name, bl.return_date - bl.expected_return_date AS overdue_days
            FROM book_loans bl
            LEFT JOIN readers r ON r.id = bl.reader_id
            LEFT JOIN books b ON b.id = bl.book_id
            WHERE bl.return_date > bl.expected_return_date AND bl.return_date IS NOT NULL;
        ''')
        self.save_to_csv(overdue_books, "overdue_books_report")
        with open(f"{self.report_dir}overdue_report.txt", 'w') as f:
            for title, reader_name, overdue_days in overdue_books:
                f.write(f"Book: {title}, Borrower: {reader_name}, Overdue days: {overdue_days}\n")

    # Отчет о количестве доступных книг на данный момент
    def report_available_books(self):
        query = """
        SELECT COUNT(*)
        FROM books b
        LEFT JOIN book_loans bl ON b.id = bl.book_id AND bl.return_date IS NULL
        WHERE bl.book_id IS NULL;
        """
        available_books = self.db.fetch_query(query)
        count = available_books[0][0]  # Получаем количество свободных книг

        print(f"Available books: {count}")

        # Сохранение результата в CSV
        self.save_to_csv([{"Available Books": count}], "available_books_report.csv")

    # Генерация GeoJSON с адресами читателей, которые еще не вернули книги
    def generate_geojson(self):

        ssl_context = ssl._create_unverified_context()
        geolocator = Nominatim(user_agent="geojson_report", ssl_context=ssl_context)

        locations = self.db.fetch_query('''
            SELECT a.city_name, a.street_name
            FROM book_loans bl
            LEFT JOIN readers r ON r.id = bl.reader_id
            LEFT JOIN addresses a ON r.address_id = a.id
            WHERE bl.return_date IS NULL;
        ''')

        features = []
        
        for city, street in locations:
            address = f"{street}, {city}"
            try:
                location = geolocator.geocode(address, timeout=10)  # Тайм-аут можно оставить
                if location:
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [location.longitude, location.latitude]
                        },
                        "properties": {
                            "city": city,
                            "street": street
                        }
                    }
                    features.append(feature)
            except GeocoderTimedOut:
                print(f"Geocoder timed out for address: {address}")

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        with open(f"{self.report_dir}readers.geojson", 'w') as f:
            json.dump(geojson, f)