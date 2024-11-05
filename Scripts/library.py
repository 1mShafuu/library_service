from datetime import date
from pydantic import BaseModel, Field
from typing import Optional


class Address(BaseModel):
    city: str
    street: str


class Author(BaseModel):
    name: str


class Book(BaseModel):
    title: str
    author_name: str
    genre: str


class Reader(BaseModel):
    name: str
    address: Address
    last_visit: date = Field(default_factory=date.today)


class Loan(BaseModel):
    book_id: int
    reader_id: int
    expected_return_date: date


class Library:
    def __init__(self, db):
        self.db = db

    def add_address(self, address: Address) -> int:
        query = """
        INSERT INTO addresses (city_name, street_name)
        VALUES (%s, %s) RETURNING id;
        """
        result = self.db.execute_query_returning(query, (address.city, address.street))
        return result[0]  # Возвращаем ID нового адреса

    def find_author_by_name(self, author_name: str) -> Optional[int]:
        query = "SELECT id FROM authors WHERE name = %s"
        author = self.db.fetch_query(query, (author_name,))
        return author[0][0] if author else None

    def add_author(self, author: Author) -> int:
        query = "INSERT INTO authors (name) VALUES (%s) RETURNING id"
        author_id = self.db.execute_query_returning(query, (author.name,))
        return author_id[0]  # Возвращаем ID нового автора

    def add_book(self, book: Book) -> None:
        author_id = self.find_author_by_name(book.author_name)
        if not author_id:
            author_id = self.add_author(Author(name=book.author_name))

        query = """
        INSERT INTO books (title, author_id, genre) 
        VALUES (%s, %s, %s)
        """
        self.db.execute_query(query, (book.title, author_id, book.genre))
        print(f"Book '{book.title}' added to database.")

    def delete_book(self, book_id: int) -> None:
        if not self.book_exists(book_id):
            print(f"Error: Book with ID {book_id} does not exist.")
            return

        if self.is_book_on_loan(book_id):
            print(f"Error: Book with ID {book_id} cannot be deleted because it is currently on loan.")
            return

        self.db.execute_query("DELETE FROM books WHERE id = %s", (book_id,))
        print(f"Book with ID {book_id} has been removed.")

    def is_book_on_loan(self, book_id: int) -> bool:
        query = "SELECT COUNT(*) FROM book_loans WHERE book_id = %s AND return_date IS NULL;"
        result = self.db.fetch_query(query, (book_id,))
        return result[0][0] > 0

    def update_book(self, book_id: int, book: Book) -> None:
        if not self.book_exists(book_id):
            print(f"Error: Book with ID {book_id} does not exist.")
            return

        author_id = self.find_author_by_name(book.author_name)
        if not author_id:
            author_id = self.add_author(Author(name=book.author_name))

        query = """
        UPDATE books
        SET title = %s, genre = %s, author_id = %s
        WHERE id = %s;
        """
        self.db.execute_query(query, (book.title, book.genre, author_id, book_id))
        print(f"Book data for ID {book_id} updated.")

    def add_reader(self, reader: Reader) -> None:
        address_id = self.add_address(reader.address)
        query = """
        INSERT INTO readers (name, address_id, last_visit)
        VALUES (%s, %s, %s);
        """
        self.db.execute_query(query, (reader.name, address_id, reader.last_visit))
        print(f"Reader '{reader.name}' added with address: {reader.address.city}, {reader.address.street}.")

    def update_reader(self, reader_id: int, reader: Reader) -> None:
        if not self.reader_exists(reader_id):
            print(f"Error: Reader with ID {reader_id} does not exist.")
            return

        address_id = self.add_address(reader.address)
        query = """
        UPDATE readers
        SET name = %s, address_id = %s, last_visit = %s
        WHERE id = %s;
        """
        self.db.execute_query(query, (reader.name, address_id, date.today(), reader_id))
        print(f"Reader data for ID {reader_id} updated.")

    def delete_reader(self, reader_id: int) -> None:
        if not self.reader_exists(reader_id):
            print(f"Error: Reader with ID {reader_id} does not exist.")
            return

        # Проверка на наличие активных займов
        query = """
        SELECT COUNT(*) FROM book_loans 
        WHERE reader_id = %s AND return_date IS NULL
        """
        result = self.db.fetch_query(query, (reader_id,))
        active_loans = result[0][0]

        if active_loans > 0:
            print(f"Error: Reader with ID {reader_id} cannot be deleted because they have active loans.")
            return

        self.db.execute_query("DELETE FROM readers WHERE id = %s", (reader_id,))
        print(f"Reader with ID {reader_id} has been removed.")

    def is_book_available(self, book_id: int) -> bool:
        # Проверяем, доступна ли книга для выдачи
        query = """
        SELECT COUNT(*) FROM book_loans
        WHERE book_id = %s AND return_date IS NULL
        """
        result = self.db.fetch_query(query, (book_id,))
        return result[0][0] == 0  # Если возвращаемое значение 0, значит книга доступна

    def add_loan(self, loan: Loan) -> None:
        try:
            if self.is_book_available(loan.book_id):
                self.db.execute_query(
                    "INSERT INTO book_loans (book_id, reader_id, loan_date, expected_return_date) VALUES (%s, %s, %s, %s)",
                    (loan.book_id, loan.reader_id, date.today(), loan.expected_return_date)
                )
            else:
                print("The book has already been issued and is not available for issue.")
        except Exception as e:
            print(f"An error occurred while adding the loan: {e}")
            self.db.conn.rollback()

    def get_active_loan(self, book_id: int, reader_id: int) -> Optional[int]:
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

    def reader_exists(self, reader_id: int) -> bool:
        query = "SELECT COUNT(*) FROM readers WHERE id = %s"
        result = self.db.fetch_query(query, (reader_id,))
        return result[0][0] > 0

    def book_exists(self, book_id: int) -> bool:
        query = "SELECT COUNT(*) FROM books WHERE id = %s"
        result = self.db.fetch_query(query, (book_id,))
        return result[0][0] > 0
