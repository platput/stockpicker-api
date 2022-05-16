from io import BytesIO

import pandas as pd

from helpers.shortlist_utils import ShortlistUtils


class ExcelManager:
    @staticmethod
    def create_excel_file_for_shortlist(shortlist_data):
        output = BytesIO()
        with pd.ExcelWriter(output) as writer:
            columns = [
                "id",
                "stock_name",
                "stock_symbol",
                "volume",
                "intraday_allowed",
                "stock_url",
                "stock_sector",
                "sector_url",
                "x-2-opening",
                "x-2-closing",
                "x-1-opening",
                "x-1-closing",
                "x-opening",
                "x-closing",
                "average_gain",
                "profit_percentage",
                "buy",
                "sell",
                "stop_loss",
                "profit_forecast"
            ]
            data = []
            for index, stock in enumerate(shortlist_data):
                data.append([
                    index,
                    stock.stock_name,
                    stock.symbol,
                    stock.volume,
                    stock.is_intraday_allowed,
                    stock.stock_url,
                    stock.stock_sector_name,
                    stock.stock_sector_url,
                    ShortlistUtils.get_starting_price_and_time(stock.price_actions[2]),
                    ShortlistUtils.get_closing_price_and_time(stock.price_actions[2]),
                    ShortlistUtils.get_starting_price_and_time(stock.price_actions[1]),
                    ShortlistUtils.get_closing_price_and_time(stock.price_actions[1]),
                    ShortlistUtils.get_starting_price_and_time(stock.price_actions[0]),
                    ShortlistUtils.get_closing_price_and_time(stock.price_actions[0]),
                    ShortlistUtils.get_average_gain(stock),
                    ShortlistUtils.get_profit_percentage(stock),
                    ShortlistUtils.get_buy_price(stock),
                    ShortlistUtils.get_sell_price(stock),
                    ShortlistUtils.get_stop_loss_price(stock),
                    ShortlistUtils.get_profit_forecast(stock)
                ])
            df = pd.DataFrame(data, columns=columns)
            df.to_excel(writer, sheet_name='Sheet1', index=False)
        return output

