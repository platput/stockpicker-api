import json
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from managers.dal.sqlalchemy import get_db
from managers.scrape_manager import ScrapeManager
from models.schemas.requests import SectorDetails
from models.schemas.responses import ScrapeMCResponse, SectorialIndicesResponse

router = APIRouter(
    prefix="/scrape",
    tags=['Data Scraping']
)


@router.get("/mc", response_model=ScrapeMCResponse)
async def scrape_mc(db: Session = Depends(get_db)):
    urls_to_scrape = {
        "9_10": "https://www.moneycontrol.com/stocks/marketstats/hourly_gain/bse/hour_1/index.php",
        "10_11": "https://www.moneycontrol.com/stocks/marketstats/hourly_gain/bse/hour_2/index.php",
        "11_12": "https://www.moneycontrol.com/stocks/marketstats/hourly_gain/bse/hour_3/index.php",
        "12_13": "https://www.moneycontrol.com/stocks/marketstats/hourly_gain/bse/hour_4/index.php",
        "13_14": "https://www.moneycontrol.com/stocks/marketstats/hourly_gain/bse/hour_5/index.php",
        "14_15": "https://www.moneycontrol.com/stocks/marketstats/hourly_gain/bse/hour_6/index.php",
        "15_16": "https://www.moneycontrol.com/stocks/marketstats/hourly_gain/bse/curr_hour/index.php"
    }
    scrape_manager = ScrapeManager(urls_to_scrape)
    try:
        response_data = scrape_manager.fetch_scraped_data(db_session=db)
        return response_data
    except (ConnectionError, AttributeError) as ce:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Data couldn't be fetched at this time. Error: {ce}")


@router.get("/update-symbols", response_model=ScrapeMCResponse)
async def update_symbols(db: Session = Depends(get_db)):
    scrape_manager = ScrapeManager(urls_to_scrape=None)
    try:
        response_data = scrape_manager.fetch_symbols_and_update(db_session=db)
        return response_data
    except (ConnectionError, AttributeError) as ce:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Data couldn't be fetched at this time. Error: {ce}")


@router.post("/mc/sector/indices", response_model=SectorialIndicesResponse)
async def scrape_sectorial_indices(sector_details_list: List[SectorDetails]):
    scrape_manager = ScrapeManager(urls_to_scrape=None)
    try:
        response_data = scrape_manager.fetch_sectorial_indices(sector_details_list)
        return response_data
    except (ConnectionError, AttributeError) as ce:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Data couldn't be fetched at this time. Error: {ce}")
