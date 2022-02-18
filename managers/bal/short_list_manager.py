import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select

from models.db.schema import PriceAction, StockName
from models.schemas.responses import ShortListResponse


class ShortListManager:
    """
    ShortListManager class
    Use this to both create the shortlists and fetch the shortlists
    """
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_short_list(self):
        """

        :return:
        """
        # datetime.now(ZoneInfo('Asia/Kolkata'))
        current_date = datetime.now(ZoneInfo('Asia/Kolkata')).date()
        # day_minus_two = current_date - timedelta(days=2)
        # day_minus_three = current_date - timedelta(days=3)
        # Get the list of stock names and their price actions for day_minus_one
        try:
            stock_names_day_one, day_one = self.__get_stocks_for_the_day(current_date)
            stock_names_day_two, day_two = self.__get_stocks_for_the_day(day_one)
            stock_names_day_three, day_three = self.__get_stocks_for_the_day(day_two)
            stocks_present_in_last_three_days = stock_names_day_one. \
                intersection(stock_names_day_two). \
                intersection(stock_names_day_three)
            short_listed_stocks = []
            for stock in stocks_present_in_last_three_days:
                # Get the price actions for three days
                stmt_one = select(PriceAction).where(StockName.stock_name == stock, PriceAction.price_date == day_one)
                stmt_two = select(PriceAction).where(StockName.stock_name == stock, PriceAction.price_date == day_two)
                stmt_three = select(PriceAction).where(StockName.stock_name == stock,
                                                       PriceAction.price_date == day_three)
                price_action_one = self.db_connection.execute(stmt_one).scalar()
                price_action_two = self.db_connection.execute(stmt_two).scalar()
                price_action_three = self.db_connection.execute(stmt_three).scalar()
                if price_action_one and price_action_two and price_action_three:
                    # Remove the hours which didn't see any price gain,
                    # this means, in the db row, it will have the value of zero
                    price_action_list_day_one = self.__get_sorted_price_action_list_with_only_gains(price_action_one)
                    price_action_list_day_two = self.__get_sorted_price_action_list_with_only_gains(price_action_two)
                    price_action_list_day_three = self.__get_sorted_price_action_list_with_only_gains(
                        price_action_three)
                    # Compare the price actions for the last three days
                    # Conditions
                    # 1. If the start price for the day_three is less than or equal to the end price for the day_three
                    # 2. If the end price for the day_three is less than or equal to the start price for the day_two
                    # 3. If the start price for the day_two is less than or equal to the end price for the day_two
                    # 4. If the end price for the day_two is less than or equal to the start price for the day_one
                    # 5. If the start price for the day_one is less than or equal to the end price for the day_one
                    if price_action_list_day_three[0].get("start", 0) <= \
                            price_action_list_day_three[-1].get("end", 0) <= \
                            price_action_list_day_two[0].get("start", 0) <= \
                            price_action_list_day_two[0].get("end", 0) <= \
                            price_action_list_day_one[0].get("start", 0) <= \
                            price_action_list_day_one[0].get("end", 0):
                        short_listed_stocks.append(stock)
            logging.info('Short list created for the day: {}'.format(current_date))
            # TODO: Save short list in the database
            return ShortListResponse(success=True, message="Successfully scraped data")
        except Exception as e:
            logging.error(f'Error while creating short list for the day: {current_date} Error: {e}')
            return ShortListResponse(success=False, message="Failed to create shortlist.")

    def __get_stocks_for_the_day(self, current_date) -> (set, datetime):
        """
        Get the list of stock names and their price actions for the current date
        :param current_date:
        :return:
        """
        stock_names_day = set()
        while True:
            current_date = (current_date - timedelta(days=1))
            stmt_one = select(StockName, PriceAction).where(
                PriceAction.price_date == current_date.strftime('%Y-%m-%d')
            )
            for stock in self.db_connection.execute(stmt_one).scalars():
                stock_names_day.add(stock.stock_name)
            if len(stock_names_day) > 0:
                break
        return stock_names_day, current_date

    @staticmethod
    def __get_sorted_price_action_list_with_only_gains(price_action) -> list:
        """
        Remove the hours which didn't see any price gain,
        :param price_action:
        :return:
        """
        price_actions = []
        if price_action.hour_1_start > 0:
            price_actions.append({"start": price_action.hour_1_start, "end": price_action.hour_1_end})
        if price_action.hour_2_start > 0:
            price_actions.append({"start": price_action.hour_2_start, "end": price_action.hour_2_end})
        if price_action.hour_3_start > 0:
            price_actions.append({"start": price_action.hour_3_start, "end": price_action.hour_3_end})
        if price_action.hour_4_start > 0:
            price_actions.append({"start": price_action.hour_4_start, "end": price_action.hour_4_end})
        if price_action.hour_5_start > 0:
            price_actions.append({"start": price_action.hour_5_start, "end": price_action.hour_5_end})
        if price_action.hour_6_start > 0:
            price_actions.append({"start": price_action.hour_6_start, "end": price_action.hour_6_end})
        if price_action.hour_7_start > 0:
            price_actions.append({"start": price_action.hour_7_start, "end": price_action.hour_7_end})
        return price_actions
