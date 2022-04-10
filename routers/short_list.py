from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from managers.bal.short_list_manager import ShortListManager
from managers.dal.sqlalchemy import get_db
from models.schemas.responses import ShortListResponse, ShortListedStocksResponse

router = APIRouter(
    prefix="/shortlist",
    tags=['Short Listing']
)


@router.get("/create", response_model=ShortListResponse)
def create_short_list(db: Session = Depends(get_db)):
    short_list_manager = ShortListManager(db)
    try:
        response_data = short_list_manager.create_short_list()
        return response_data
    except (ConnectionError, AttributeError) as ce:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Data couldn't be fetched at this time. Error: {ce}")


@router.get("/get/latest", response_model=ShortListedStocksResponse)
def get_short_list(db: Session = Depends(get_db)):
    short_list_manager = ShortListManager(db)
    try:
        response_data = short_list_manager.fetch_short_list()
        return response_data
    except (ConnectionError, AttributeError) as ce:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Data couldn't be fetched at this time. Error: {ce}")


@router.get("/get/{offset}", response_model=ShortListedStocksResponse)
async def get_short_list(offset: int, db: Session = Depends(get_db)):
    short_list_manager = ShortListManager(db)
    try:
        response_data = short_list_manager.fetch_short_list(offset)
        return response_data
    except (ConnectionError, AttributeError) as ce:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Data couldn't be fetched at this time. Error: {ce}")


@router.get("/download/{offset}")
async def download_short_list(offset: int = 0, db: Session = Depends(get_db)):
    short_list_manager = ShortListManager(db)
    try:
        return short_list_manager.download_short_list(offset)
    except (ConnectionError, AttributeError) as ce:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"File couldn't be downloaded at this time. Error: {ce}")
