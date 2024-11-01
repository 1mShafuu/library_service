from library import Book, Reader, Address, Loan
from pydantic import ValidationError
from datetime import datetime, date


def main_menu(library, reports):
    while True:
        print("\nMain Menu")
        print("1. Add/Remove/Update Book")
        print("2. Add/Remove/Update Reader")
        print("3. Add/Return Book Loan")
        print("4. View Reports")
        print("5. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            book_menu(library)
        elif choice == '2':
            reader_menu(library)
        elif choice == '3':
            loan_menu(library)
        elif choice == '4':
            report_menu(reports)
        elif choice == '5':
            break
        else:
            print("Invalid option, please try again.")


def book_menu(library):
    while True:
        print("\nBook Menu")
        print("1. Add Book")
        print("2. Remove Book")
        print("3. Update Book")
        print("4. Back to Main Menu")
        choice = input("Select an option: ")

        if choice == '1':
            title = input("Enter book title: ")
            if not is_valid_name(title):
                print("Invalid book title, please try again.")
                continue

            author_name = input("Enter author name: ")
            if not is_valid_name(author_name):
                print("Invalid author name, please try again.")
                continue

            genre = input("Enter book genre: ")
            if not is_valid_name(genre):
                print("Invalid book genre, please try again.")
                continue

            library.add_book(Book(title=title, author_name=author_name, genre=genre))
        elif choice == '2':
            book_id = input("Enter book ID to remove: ")
            if not is_valid_id(book_id):
                print("Invalid ID. Please enter a valid book ID.")
                continue
            library.delete_book(int(book_id))
        elif choice == '3':
            book_id = input("Enter book ID to update: ")
            if not is_valid_id(book_id):
                print("Invalid ID. Please enter a valid book ID.")
                continue

            title = input("Enter book title: ")
            if not is_valid_name(title):
                print("Invalid book title, please try again.")
                continue

            genre = input("Enter book genre: ")
            if not is_valid_name(genre):
                print("Invalid book genre, please try again.")
                continue

            author_name = input("Enter author name: ")
            if not is_valid_name(author_name):
                print("Invalid author name, please try again.")
                continue

            library.update_book(int(book_id), Book(title=title, author_name=author_name, genre=genre))
        elif choice == '4':
            break
        else:
            print("Invalid option, please try again.")


def reader_menu(library):
    while True:
        print("\nReader Menu")
        print("1. Add Reader")
        print("2. Remove Reader")
        print("3. Update Reader")
        print("4. Back to Main Menu")
        choice = input("Select an option: ")

        if choice == '1':
            name = input("Enter reader name: ")
            if not is_valid_name(name):
                print("Invalid name. Please enter a valid name.")
                continue

            city = input("Enter reader city: ")
            if not is_valid_address(city):
                print("Invalid city. Please enter a valid city.")
                continue

            street = input("Enter reader street (Street name + St) : ")
            if not is_valid_street(street):
                print("Invalid street. Please enter a valid street.")
                continue

            library.add_reader(Reader(name=name, address=Address(city=city, street=street)))
        elif choice == '2':
            reader_id = input("Enter reader ID to remove: ")
            if not is_valid_id(reader_id):
                print("Invalid ID. Please enter a valid reader ID.")
                continue
            library.delete_reader(int(reader_id))
        elif choice == '3':
            reader_id = input("Enter reader ID to update: ")
            if not is_valid_id(reader_id):
                print("Invalid ID. Please enter a valid reader ID.")
                continue

            name = input("Enter new reader name: ")
            if not is_valid_name(name):
                print("Invalid name. Please enter a valid name.")
                continue

            city = input("Enter new reader city: ")
            if not is_valid_address(city):
                print("Invalid city. Please enter a valid city.")
                continue

            street = input("Enter new reader street (Street name + St): ")
            if not is_valid_street(street):
                print("Invalid street. Please enter a valid street.")
                continue

            library.update_reader(int(reader_id), Reader(name=name, address=Address(city=city, street=street)))
        elif choice == '4':
            break
        else:
            print("Invalid option, please try again.")


def loan_menu(library):
    while True:
        print("\nLoan Menu")
        print("1. Add Book Loan")
        print("2. Return Book Loan")
        print("3. Back to Main Menu")
        choice = input("Select an option: ")

        if choice == '1':
            try:
                book_id = input("Enter book ID: ")
                if not is_valid_id(book_id):
                    print("Invalid book ID. Please enter a valid integer ID.")
                    continue
                book_id = int(book_id)

                reader_id = input("Enter reader ID: ")
                if not is_valid_id(reader_id):
                    print("Invalid reader ID. Please enter a valid integer ID.")
                    continue
                reader_id = int(reader_id)

                expected_return_date_str = input("Enter expected return date (YYYY-MM-DD): ")
                expected_return_date = datetime.strptime(expected_return_date_str, "%Y-%m-%d").date()

                if expected_return_date <= date.today():
                    print("Error: The return date must be in the future.")
                    continue

                # Проверяем существование книги
                if not library.book_exists(book_id):
                    print(f"Error: Book with ID {book_id} does not exist.")
                    continue

                # Проверяем существование читателя
                if not library.reader_exists(reader_id):
                    print(f"Error: Reader with ID {reader_id} does not exist.")
                    continue

                # Проверяем, доступна ли книга для аренды
                if not library.is_book_available(book_id):
                    print("This book is currently not available for loan.")
                    continue

                # Создаем объект Loan и добавляем его
                loan = Loan(book_id=book_id, reader_id=reader_id, expected_return_date=expected_return_date)
                library.add_loan(loan)
                print("The book loan was successful")

            except ValidationError as e:
                print(
                    f"Validation error: {e}. Please ensure the expected return date is in the correct format ("
                    f"YYYY-MM-DD).")
            except ValueError:
                print("Invalid input. Please enter valid integers for book ID and reader ID.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        elif choice == '2':
            try:
                book_id = int(input("Enter book ID: "))
                reader_id = int(input("Enter reader ID: "))

                # Возвращаем заем
                library.return_loan(book_id, reader_id)

            except ValueError:
                print("Invalid input. Please enter valid integers for book ID and reader ID.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        elif choice == '3':
            break
        else:
            print("Invalid option, please try again.")


def report_menu(reports):
    while True:
        print("\nReport Menu")
        print("1. Report on Available Books")
        print("2. Books Borrowed by Each Reader")
        print("3. Books Currently on Loan")
        print("4. Last Visit Date of Each Reader")
        print("5. Favorite Genre of Each Reader")
        print("6. Generate GeoJSON Report")
        print("10. Back to Main Menu")
        choice = input("Select an option: ")

        if choice == '1':
            reports.report_available_books()
        elif choice == '2':
            reports.report_reader_history()
        elif choice == '3':
            reports.report_current_loans()
        elif choice == '4':
            reports.report_last_visit()
        elif choice == '5':
            reports.report_favorite_genre_by_reader()
        elif choice == '6':
            reports.generate_geojson()
        elif choice == '10':
            break
        else:
            print("Invalid option, please try again.")


def is_valid_name(name: str) -> bool:
    return bool(name) and all(char.isalpha() or char.isspace() for char in name)


def is_valid_address(address: str) -> bool:
    return bool(address)


def is_valid_street(street: str) -> bool:
    return bool(street)


def is_valid_id(input_id: str) -> bool:
    return input_id.isdigit() and int(input_id) > 0
