from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from managers.bal.short_list_manager import ShortListManager
from managers.dal.sqlalchemy import get_db
from models.schemas.responses import ShortListResponse

router = APIRouter(
    prefix="/shortlist",
    tags=['Short Listing']
)


@router.get("/create", response_model=ShortListResponse)
def create_short_list(db: Session = Depends(get_db)):
    short_list_manager = ShortListManager()
    try:
        response_data = short_list_manager.create_short_list(db_session=db)
        return response_data
    except (ConnectionError, AttributeError) as ce:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Data couldn't be fetched at this time. Error: {ce}")
