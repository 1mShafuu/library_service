from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Book, Reader, Loan, Address, Author, ArchivedBook
from app.schemas import BookCreate, ReaderCreate, ReaderUpdate, LoanCreate, BookUpdate
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class LibraryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # === Address Operations ===
    async def _get_or_create_address(self, city: str, street: str) -> int:
        result = await self.db.execute(
            select(Address.id).where(and_(Address.city == city, Address.street == street))
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
        author = await self._get_or_create_author(book_data.author_name)

        book = Book(
            title=book_data.title,
            genre=book_data.genre,
            author_id=author.id,
            is_available=True
        )
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)

        result = await self.db.execute(
            select(Book).options(selectinload(Book.author)).where(Book.id == book.id)
        )
        return result.scalar_one()

    async def _get_or_create_author(self, author_name: str) -> Author:
        result = await self.db.execute(select(Author).where(Author.name == author_name))
        author = result.scalar_one_or_none()
        if not author:
            author = Author(name=author_name)
            self.db.add(author)
            await self.db.commit()
            await self.db.refresh(author)
        return author

    async def get_book(self, book_id: int) -> Optional[Book]:
        result = await self.db.execute(
            select(Book).options(selectinload(Book.author)).where(Book.id == book_id)
        )
        return result.scalar_one_or_none()

    async def update_book(self, book_id: int, book_data: BookUpdate) -> Book:
        book = await self.get_book(book_id)
        if not book:
            raise ValueError("Book not found")

        if book_data.title is not None:
            book.title = book_data.title
        if book_data.genre is not None:
            book.genre = book_data.genre
        if book_data.author_name is not None:
            author = await self._get_or_create_author(book_data.author_name)
            book.author_id = author.id

        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete_book(self, book_id: int) -> None:
        result = await self.db.execute(
            select(Book).options(selectinload(Book.author), selectinload(Book.loans)).where(Book.id == book_id)
        )
        book = result.scalar_one_or_none()

        if not book:
            raise HTTPException(status_code=404, detail="Книга не найдена")

        for loan in book.loans:
            if loan.return_date is None:
                raise HTTPException(
                    status_code=400,
                    detail="Нельзя удалить книгу: она всё ещё в займе",
                )

        # Архивируем книгу перед удалением
        archived_book = ArchivedBook(
            original_book_id=book.id,
            title=book.title,
            genre=book.genre,
            author_name=book.author.name
        )
        self.db.add(archived_book)

        # Удаляем саму книгу
        await self.db.delete(book)
        await self.db.commit()

    async def get_available_books(self) -> List[Book]:
        result = await self.db.execute(
            select(Book).options(selectinload(Book.author)).where(Book.is_available == True)
        )
        return result.scalars().all()

    # === Reader Operations ===
    async def create_reader(self, reader_data: ReaderCreate) -> Reader:
        address = Address(**reader_data.address.model_dump())
        self.db.add(address)
        await self.db.flush()

        reader = Reader(name=reader_data.name, address=address, last_visit=datetime.utcnow())
        self.db.add(reader)
        await self.db.flush()
        reader_id = reader.id
        await self.db.commit()

        stmt = select(Reader).options(selectinload(Reader.address)).where(Reader.id == reader_id)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_reader(self, reader_id: int) -> Optional[Reader]:
        result = await self.db.execute(
            select(Reader).options(selectinload(Reader.address)).where(Reader.id == reader_id)
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

    async def delete_reader(self, reader_id: int) -> None:
        result = await self.db.execute(
            select(Loan).where(and_(Loan.reader_id == reader_id, Loan.return_date == None))
        )
        if result.scalar_one_or_none():
            raise ValueError("Cannot delete a reader with active loans")

        await self.db.execute(delete(Reader).where(Reader.id == reader_id))
        await self.db.commit()

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
        result = await self.db.execute(select(Loan).where(Loan.id == loan_id))
        loan = result.scalar_one_or_none()

        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")

        if loan.return_date is not None:
            logger.warning(f"Attempt to return already returned loan (id={loan_id}) on {date.today()}")
            raise HTTPException(status_code=409, detail="Book has already been returned")

        loan.return_date = date.today()

        book = await self.get_book(loan.book_id)
        if book:
            book.is_available = True

        await self.db.commit()
        await self.db.refresh(loan)
        return loan
