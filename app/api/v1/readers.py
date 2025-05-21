from fastapi import APIRouter, Depends, HTTPException, Path, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import LibraryService
from app.schemas import ReaderCreate, ReaderUpdate, ReaderResponse
from app.db.session import get_db

router = APIRouter(tags=["readers"])


@router.post("/", response_model=ReaderResponse)
async def create_reader(
    reader_data: ReaderCreate,
    db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    try:
        reader = await service.create_reader(reader_data)
        return ReaderResponse.model_validate(reader)  # ✅ ручная валидация
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{reader_id}", response_model=ReaderResponse)
async def get_reader(
    reader_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    reader = await service.get_reader(reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    return ReaderResponse.model_validate(reader)


@router.put("/{reader_id}", response_model=ReaderResponse)
async def update_reader(
    reader_id: int,
    reader_data: ReaderUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    try:
        updated_reader = await service.update_reader(reader_id, reader_data)
        return ReaderResponse.model_validate(updated_reader)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{reader_id}", status_code=204)
async def delete_reader(
        reader_id: int = Path(..., ge=1),
        db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    try:
        await service.delete_reader(reader_id)
        return Response(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))