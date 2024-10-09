from datetime import date

class Library:
    def __init__(self, db):
        self.db = db

    def add_address(self, city, street):
        query = """
        INSERT INTO addresses (city_name, street_name)
        VALUES (%s, %s) RETURNING id;
        """
        result = self.db.execute_query(query, (city, street))
        return result[0] 

    def find_author_by_name(self, author_name):
        query = "SELECT id FROM authors WHERE name = %s"
        author = self.db.fetch_query(query, (author_name,))  
        return author[0][0] if author else None

    def add_author(self, author_name):
        query = "INSERT INTO authors (name) VALUES (%s) RETURNING id"
        author_id = self.db.execute_query(query, (author_name,)) 
        return author_id[0] 

    def add_book(self, title, author_name, genre):
        author_id = self.find_author_by_name(author_name)

        if not author_id:
            author_id = self.add_author(author_name)

        query = """
        INSERT INTO books (title, author_id, genre) 
        VALUES (%s, %s, %s)
        """
        self.db.execute_query(query, (title, author_id, genre)) 
        print(f"Книга '{title}' добавлена в базу данных.")

    def delete_book(self, book_id):
        self.db.execute_query("DELETE FROM books WHERE id = %s", (book_id,))

    def update_book(self, book_id, title, genre, author_name):
        author_id = self.find_author_by_name(author_name)
        if not author_id:
            author_id = self.add_author(author_name)

        self.db.execute_query(
            "UPDATE books SET title = %s, genre = %s, author_id = %s WHERE id = %s",
            (title, genre, author_id, book_id)
        )

    def add_reader(self, name, city, street):
        address_id = self.add_address(city, street)
        query = """
        INSERT INTO readers (name, address_id, last_visit)
        VALUES (%s, %s, %s);
        """
        self.db.execute_query(query, (name, address_id, date.today()))
        print(f"Читатель '{name}' добавлен с адресом: {city}, {street}.")

    def update_reader(self, reader_id, name, city, street):
        address_id = self.add_address(city, street)
        query = """
        UPDATE readers
        SET name = %s, address_id = %s, last_visit = %s
        WHERE id = %s;
        """
        self.db.execute_query(query, (name, address_id, date.today(), reader_id))
        print(f"Данные читателя '{name}' обновлены.")

    def delete_reader(self, reader_id):
        self.db.execute_query("DELETE FROM readers WHERE id = %s", (reader_id,))

    def is_book_available(self, book_id):
        # Проверяем, доступна ли книга для выдачи
        query = """
        SELECT COUNT(*) FROM book_loans
        WHERE book_id = %s AND return_date IS NULL
        """
        result = self.db.fetch_query(query, (book_id,))
        return result[0][0] == 0  # Если возвращаемое значение 0, значит книга доступна

    def add_loan(self, book_id, reader_id, expected_return_date):
        if self.is_book_available(book_id):
            self.db.execute_query(
                "INSERT INTO book_loans (book_id, reader_id, loan_date, expected_return_date) VALUES (%s, %s, %s, %s)",
                (book_id, reader_id, date.today(), expected_return_date)
            )
            print("Книга успешно выдана.")
        else:
            print("Книга уже выдана и недоступна для выдачи.")

    def get_active_loan(self, book_id, reader_id):
        # Получаем активный займ для конкретной книги и читателя
        query = """
        SELECT id FROM book_loans
        WHERE book_id = %s AND reader_id = %s AND return_date IS NULL
        """
        result = self.db.fetch_query(query, (book_id, reader_id))
        return result[0][0] if result else None

    def return_loan(self, book_id, reader_id):
        # Возвращаем книгу по идентификатору книги и читателя
        loan_id = self.get_active_loan(book_id, reader_id)

        if loan_id:
            self.db.execute_query(
                "UPDATE book_loans SET return_date = %s WHERE id = %s",
                (date.today(), loan_id)
            )
            print("Книга успешно возвращена.")
        else:
            print("Ошибка: либо книга не была взята, либо она уже возвращена.")