from fastapi import APIRouter, Depends, HTTPException, Path, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List

from app.services import LibraryService
from app.db.session import get_db
from app.schemas import BookCreate, BookUpdate, BookResponse
from app.models import Book

router = APIRouter()


@router.post("/", response_model=BookResponse)
async def create_book(
        book_data: BookCreate,
        db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    try:
        created_book = await service.create_book(book_data)

        result = await db.execute(
            select(Book)
            .options(selectinload(Book.author))
            .where(Book.id == created_book.id)
        )
        book_with_author = result.scalar_one()

        return BookResponse.model_validate(book_with_author)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/available", response_model=List[BookResponse])
async def list_available_books(
        db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    books = await service.get_available_books()
    return [BookResponse.model_validate(b) for b in books]


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
        book_id: int,
        book_data: BookUpdate,
        db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    try:
        updated_book = await service.update_book(book_id, book_data)

        result = await db.execute(
            select(Book)
            .options(selectinload(Book.author))
            .where(Book.id == updated_book.id)
        )
        book_with_author = result.scalar_one()

        return BookResponse.model_validate(book_with_author)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{book_id}", status_code=204)
async def delete_book(
        book_id: int = Path(..., ge=1),
        db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    try:
        await service.delete_book(book_id)
        return Response(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
