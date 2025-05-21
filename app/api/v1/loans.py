from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import LibraryService
from app.schemas import LoanCreate, LoanResponse
from app.db.session import get_db

router = APIRouter(tags=["loans"])

@router.post("/", response_model=LoanResponse)
async def create_loan(
    loan_data: LoanCreate,
    db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    try:
        return await service.create_loan(loan_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{loan_id}/return", response_model=LoanResponse)
async def return_loan(
    loan_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = LibraryService(db)
    try:
        return await service.return_loan(loan_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))