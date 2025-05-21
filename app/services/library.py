from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Book, Reader, Loan, Address, Author
from app.schemas import BookCreate, ReaderCreate, ReaderUpdate, LoanCreate, BookUpdate
from fastapi import HTTPException

class LibraryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # === Address Operations ===
    async def _get_or_create_address(self, city: str, street: str) -> int:
        result = await self.db.execute(
            select(Address.id)
            .where(and_(
                Address.city == city,
                Address.street == street
            ))
        )
        address_id = result.scalar_one_or_none()

        if not address_id:
            new_address = Address(city=city, street=street)
            self.db.add(new_address)
            await self.db.commit()
            await self.db.refresh(new_address)
            address_id = new_address.id

        return address_id

    # === Book Operations ===
    async def create_book(self, book_data: BookCreate) -> Book:
        result = await self.db.execute(
            select(Author).where(Author.name == book_data.author_name)
        )
        author = result.scalar_one_or_none()

        if not author:
            author = Author(name=book_data.author_name)
            self.db.add(author)
            await self.db.commit()
            await self.db.refresh(author)

        book = Book(
            title=book_data.title,
            genre=book_data.genre,
            author_id=author.id,
            is_available=True
        )
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)

        # Подгружаем связанного автора для from_orm
        result = await self.db.execute(
            select(Book).options(selectinload(Book.author)).where(Book.id == book.id)
        )
        return result.scalar_one()

    async def get_book(self, book_id: int) -> Optional[Book]:
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.author))
            .where(Book.id == book_id)
        )
        return result.scalar_one_or_none()

    # === Reader Operations ===
    async def create_reader(self, reader_data: ReaderCreate) -> Reader:
        address = Address(**reader_data.address.model_dump())
        self.db.add(address)
        await self.db.flush()

        reader = Reader(name=reader_data.name, address=address, last_visit=datetime.utcnow())
        self.db.add(reader)
        await self.db.flush()
        reader_id = reader.id  # теперь id точно есть
        await self.db.commit()

        stmt = select(Reader).options(selectinload(Reader.address)).where(Reader.id == reader_id)
        result = await self.db.execute(stmt)
        reader_with_address = result.scalar_one()
        return reader_with_address

    async def get_reader(self, reader_id: int) -> Optional[Reader]:
        result = await self.db.execute(
            select(Reader)
            .options(selectinload(Reader.address))
            .where(Reader.id == reader_id)
        )
        reader = result.scalar_one_or_none()
        if reader:
            reader.last_visit = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(reader)
        return reader

    async def update_reader(self, reader_id: int, reader_data: ReaderUpdate) -> Reader:
        reader = await self.get_reader(reader_id)
        if not reader:
            raise ValueError("Reader not found")

        address_id = await self._get_or_create_address(
            reader_data.address.city,
            reader_data.address.street
        )

        reader.name = reader_data.name
        reader.address_id = address_id
        reader.last_visit = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(reader)
        return reader

    # === Loan Operations ===
    async def create_loan(self, loan_data: LoanCreate) -> Loan:
        AVERAGE_LOAN_PERIOD_BY_WEEKS = 2
        book = await self.get_book(loan_data.book_id)
        if not book or not book.is_available:
            raise ValueError("Book not available or already loaned out")

        reader = await self.get_reader(loan_data.reader_id)
        if not reader:
            raise ValueError("Reader not found")

        today = date.today()
        expected_return = today + timedelta(weeks=AVERAGE_LOAN_PERIOD_BY_WEEKS)

        loan = Loan(
            book_id=loan_data.book_id,
            reader_id=loan_data.reader_id,
            loan_date=today,
            expected_return_date=expected_return
        )

        book.is_available = False
        self.db.add(loan)
        await self.db.commit()
        await self.db.refresh(loan)
        return loan

    async def return_loan(self, loan_id: int) -> Loan:
        result = await self.db.execute(
            select(Loan)
            .where(Loan.id == loan_id)
        )
        loan = result.scalar_one_or_none()

        if not loan:
            raise ValueError("Loan not found")

        loan.return_date = date.today()
        book = await self.get_book(loan.book_id)
        if book:
            book.is_available = True

        await self.db.commit()
        await self.db.refresh(loan)
        return loan

    #####
    # === Book update ===
    async def update_book(self, book_id: int, book_data: BookUpdate) -> Book:
        book = await self.get_book(book_id)
        if not book:
            raise ValueError("Book not found")

        # Обновляем поля книги из book_data, если они переданы
        if book_data.title is not None:
            book.title = book_data.title
        if book_data.genre is not None:
            book.genre = book_data.genre

        # Обновление автора (если нужно)
        if book_data.author_name is not None:
            result = await self.db.execute(select(Author).where(Author.name == book_data.author_name))
            author = result.scalar_one_or_none()
            if not author:
                author = Author(name=book_data.author_name)
                self.db.add(author)
                await self.db.commit()
                await self.db.refresh(author)
            book.author_id = author.id

        await self.db.commit()
        await self.db.refresh(book)
        return book

    # === Book delete ===
    async def delete_book(self, book_id: int) -> None:
        # Получаем книгу вместе с займами
        result = await self.db.execute(
            select(Book).options(selectinload(Book.loans)).where(Book.id == book_id)
        )
        book = result.scalar_one_or_none()

        if book is None:
            raise HTTPException(status_code=404, detail="Книга не найдена")

        # Проверяем, есть ли незавершенные займы
        for loan in book.loans:
            if loan.return_date is None:
                raise HTTPException(
                    status_code=400,
                    detail="Нельзя удалить книгу: она всё ещё в займе",
                )

        await self.db.delete(book)
        await self.db.commit()

    # === Reader delete ===
    async def delete_reader(self, reader_id: int) -> None:
        # Проверяем активные займы
        result = await self.db.execute(
            select(Loan).where(and_(Loan.reader_id == reader_id, Loan.return_date == None))
        )
        active_loan = result.scalar_one_or_none()
        if active_loan:
            raise ValueError("Cannot delete a reader with active loans")

        await self.db.execute(delete(Reader).where(Reader.id == reader_id))
        await self.db.commit()

    # === Get available books ===
    async def get_available_books(self) -> List[Book]:
        result = await self.db.execute(
            select(Book).options(selectinload(Book.author)).where(Book.is_available == True)
        )
        books = result.scalars().all()
        return books
