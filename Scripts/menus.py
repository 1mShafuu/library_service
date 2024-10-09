from library import Library
from reports import Reports

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
            author_name = input("Enter author name: ")
            genre = input("Enter book genre: ")
            library.add_book(title, author_name, genre)
        elif choice == '2':
            book_id = int(input("Enter book ID to remove: "))
            library.delete_book(book_id)
        elif choice == '3':
            book_id = int(input("Enter book ID to update: "))
            title = input("Enter new book title: ")
            genre = input("Enter new book genre: ")
            author_id = int(input("Enter new author ID: "))
            library.update_book(book_id, title, genre, author_id)
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
            address = input("Enter reader address: ")
            library.add_reader(name, address)
        elif choice == '2':
            reader_id = int(input("Enter reader ID to remove: "))
            library.delete_reader(reader_id)
        elif choice == '3':
            reader_id = int(input("Enter reader ID to update: "))
            name = input("Enter new reader name: ")
            address = input("Enter new reader address: ")
            library.update_reader(reader_id, name, address)
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
            book_id = int(input("Enter book ID: "))
            reader_id = int(input("Enter reader ID: "))
            expected_return_date = input("Enter expected return date (YYYY-MM-DD): ")
            library.add_loan(book_id, reader_id, expected_return_date)
        elif choice == '2':
            book_id = int(input("Enter book ID: "))
            reader_id = int(input("Enter reader ID: "))
            library.return_loan(book_id, reader_id)
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
