import json
from datetime import datetime
from zoneinfo import ZoneInfo

from helpers.constants import Constants
from models.db.schema import PriceAction, StockName
import uuid


class PriceActionDataManager:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def add_price_actions_to_db(self, data):
        for price_action in data:
            price_action_obj = PriceAction()
            price_action_obj.id = uuid.uuid4()
            stock_name = price_action.get(Constants.STOCK_NAME)
            price_action_obj.stock_id = self.get_stock_from_db(stock_name).id
            fetched_date = price_action.get(Constants.DATE)
            fetched_date = datetime.fromisoformat(fetched_date).date().strftime('%Y-%m-%d')
            price_action_obj.price_date = fetched_date
            stock_details = price_action.get(Constants.STOCK_DETAILS)
            for stock in stock_details:
                time_period = stock.get(Constants.TIME_PERIOD)
                match time_period:
                    case Constants.NINE_TO_TEN:
                        price_action_obj.hour_1_start = stock.get(Constants.STARTING_PRICE)
                        price_action_obj.hour_1_end = stock.get(Constants.ENDING_PRICE)
                    case Constants.TEN_TO_ELEVEN:
                        price_action_obj.hour_2_start = stock.get(Constants.STARTING_PRICE)
                        price_action_obj.hour_2_end = stock.get(Constants.ENDING_PRICE)
                    case Constants.ELEVEN_TO_TWELVE:
                        price_action_obj.hour_3_start = stock.get(Constants.STARTING_PRICE)
                        price_action_obj.hour_3_end = stock.get(Constants.ENDING_PRICE)
                    case Constants.TWELVE_TO_THIRTEEN:
                        price_action_obj.hour_4_start = stock.get(Constants.STARTING_PRICE)
                        price_action_obj.hour_4_end = stock.get(Constants.ENDING_PRICE)
                    case Constants.THIRTEEN_TO_FOURTEEN:
                        price_action_obj.hour_5_start = stock.get(Constants.STARTING_PRICE)
                        price_action_obj.hour_5_end = stock.get(Constants.ENDING_PRICE)
                    case Constants.FOURTEEN_TO_FIFTEEN:
                        price_action_obj.hour_6_start = stock.get(Constants.STARTING_PRICE)
                        price_action_obj.hour_6_end = stock.get(Constants.ENDING_PRICE)
                    case Constants.FIFTEEN_TO_SIXTEEN:
                        price_action_obj.hour_7_start = stock.get(Constants.STARTING_PRICE)
                        price_action_obj.hour_7_end = stock.get(Constants.ENDING_PRICE)
            price_action_obj.created_at = datetime.now(ZoneInfo('Asia/Kolkata'))
            self.db_connection.add(price_action_obj)
        self.db_connection.commit()

    def add_new_stock_names_to_db(self, data):
        for stock in data:
            stock_obj = StockName()
            stock_obj.stock_id = uuid.uuid4()
            stock_obj.stock_name = stock.get(Constants.STOCK_NAME)
            self.db_connection.add(stock)
        self.db_connection.commit()

    def get_stock_from_db(self, stock_name):
        stock_obj = StockName()
        stock_obj.stock_name = stock_name
        return self.db_connection.query(stock_obj).first()

