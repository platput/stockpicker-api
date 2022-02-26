from datetime import datetime
from zoneinfo import ZoneInfo

from helpers.constants import Constants
from models.schemas.responses import MCData, MCDataDetails, ScrapeMCResponse


class DataManager:
    # @staticmethod
    # def convert_scrapped_mc_data_to_response_model(scraped_mc_data):
    #     response = ScrapeMCResponse(success=True, message="Successfully scraped data", data=[])
    #     for stock_name, stock_details in scraped_mc_data.items():
    #         mc_data = MCData(stock_name=stock_name, stock_details=[], date=datetime.now(ZoneInfo('Asia/Kolkata')))
    #         for item in stock_details:
    #             mc_data_details = MCDataDetails(
    #                 time_period=item["time_period"],
    #                 starting_price=item["starting_price"],
    #                 ending_price=item["ending_price"])
    #             mc_data.stock_details.append(mc_data_details)
    #         response.data.append(mc_data)
    #     return response

    @staticmethod
    def format_scrapped_mc_data(scraped_mc_data):
        formatted_data = []
        for stock_name, stock_details in scraped_mc_data.items():
            mc_data = {
                Constants.STOCK_NAME: stock_name,
                Constants.STOCK_DETAILS_URL: stock_details[Constants.STOCK_DETAILS_URL],
                Constants.STOCK_DETAILS: [],
                Constants.DATE: datetime.now(ZoneInfo(Constants.TIME_ZONE))
            }
            for item in stock_details.get(Constants.PRICE_ACTION, []):
                mc_data_details = {
                    Constants.TIME_PERIOD: item[Constants.TIME_PERIOD],
                    Constants.STARTING_PRICE: item[Constants.STARTING_PRICE],
                    Constants.ENDING_PRICE: item[Constants.ENDING_PRICE]
                }
                mc_data[Constants.STOCK_DETAILS].append(mc_data_details)
            formatted_data.append(mc_data)
        return formatted_data
