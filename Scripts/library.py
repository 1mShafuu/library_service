from datetime import date
from typing import Optional, List, Tuple

class Library:
    def __init__(self, db):
        self.db = db

    def add_address(self, city: str, street: str) -> int:
        query = """
        INSERT INTO addresses (city_name, street_name)
        VALUES (%s, %s) RETURNING id;
        """
        result = self.db.execute_query(query, (city, street))
        return result[0]  # Возвращаем ID нового адреса

    def find_author_by_name(self, author_name: str) -> Optional[int]:
        query = "SELECT id FROM authors WHERE name = %s"
        author = self.db.fetch_query(query, (author_name,))
        return author[0][0] if author else None

    def add_author(self, author_name: str) -> int:
        query = "INSERT INTO authors (name) VALUES (%s) RETURNING id"
        author_id = self.db.execute_query(query, (author_name,))
        return author_id[0]  # Возвращаем ID нового автора

    def add_book(self, title: str, author_name: str, genre: str) -> None:
        author_id = self.find_author_by_name(author_name)
        if not author_id:
            author_id = self.add_author(author_name)

        query = """
        INSERT INTO books (title, author_id, genre) 
        VALUES (%s, %s, %s)
        """
        self.db.execute_query(query, (title, author_id, genre))
        print(f"Book '{title}' added to database.")

    def delete_book(self, book_id: int) -> None:
        self.db.execute_query("DELETE FROM books WHERE id = %s", (book_id,))

    def update_book(self, book_id: int, title: str, genre: str, author_name: str) -> None:
        author_id = self.find_author_by_name(author_name)
        if not author_id:
            author_id = self.add_author(author_name)

        self.db.execute_query(
            "UPDATE books SET title = %s, genre = %s, author_id = %s WHERE id = %s",
            (title, genre, author_id, book_id)
        )

    def add_reader(self, name: str, city: str, street: str) -> None:
        address_id = self.add_address(city, street)
        query = """
        INSERT INTO readers (name, address_id, last_visit)
        VALUES (%s, %s, %s);
        """
        self.db.execute_query(query, (name, address_id, date.today()))
        print(f"Reader '{name}' added with address: {city}, {street}.")

    def update_reader(self, reader_id: int, name: str, city: str, street: str) -> None:
        address_id = self.add_address(city, street)
        query = """
        UPDATE readers
        SET name = %s, address_id = %s, last_visit = %s
        WHERE id = %s;
        """
        self.db.execute_query(query, (name, address_id, date.today(), reader_id))
        print(f"Reader data '{name}' updated.")

    def delete_reader(self, reader_id: int) -> None:
        self.db.execute_query("DELETE FROM readers WHERE id = %s", (reader_id,))

    def is_book_available(self, book_id: int) -> bool:
        # Проверяем, доступна ли книга для выдачи
        query = """
        SELECT COUNT(*) FROM book_loans
        WHERE book_id = %s AND return_date IS NULL
        """
        result = self.db.fetch_query(query, (book_id,))
        return result[0][0] == 0  # Если возвращаемое значение 0, значит книга доступна

    def add_loan(self, book_id: int, reader_id: int, expected_return_date: date) -> None:
        if self.is_book_available(book_id):
            self.db.execute_query(
                "INSERT INTO book_loans (book_id, reader_id, loan_date, expected_return_date) VALUES (%s, %s, %s, %s)",
                (book_id, reader_id, date.today(), expected_return_date)
            )
            print("The book has been successfully issued.")
        else:
            print("The book has already been issued and is not available for issue.")

    def get_active_loan(self, book_id: int, reader_id: int) -> Optional[int]:
        # Получаем активный займ для конкретной книги и читателя
        query = """
        SELECT id FROM book_loans
        WHERE book_id = %s AND reader_id = %s AND return_date IS NULL
        """
        result = self.db.fetch_query(query, (book_id, reader_id))
        return result[0][0] if result else None

    def return_loan(self, book_id: int, reader_id: int) -> None:
        # Возвращаем книгу по идентификатору книги и читателя
        loan_id = self.get_active_loan(book_id, reader_id)

        if loan_id:
            self.db.execute_query(
                "UPDATE book_loans SET return_date = %s WHERE id = %s",
                (date.today(), loan_id)
            )
            print("The book was successfully returned.")
        else:
            print("Error: either the book was not taken, or it has already been returned.")
