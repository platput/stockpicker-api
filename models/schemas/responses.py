from datetime import datetime
from pydantic import BaseModel, Field

# Schema for money control data
from typing import List


class MCDataDetails(BaseModel):
    time_period: str
    starting_price: str
    ending_price: str


class MCData(BaseModel):
    stock_name: str
    stock_details: List[MCDataDetails]
    date: datetime


# Response model for /scrape/mc endpoint
class ScrapeMCResponse(BaseModel):
    success: bool
    message: str

