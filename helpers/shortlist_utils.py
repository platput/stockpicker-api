class ShortlistUtils:
    @staticmethod
    def get_non_zero_hourly_prices(price_action):
        hourly_prices = [
            {"time": 9, "price": price_action.hour_1_start},
            {"time": 10, "price": price_action.hour_1_end},
            {"time": 10, "price": price_action.hour_2_start},
            {"time": 11, "price": price_action.hour_2_end},
            {"time": 11, "price": price_action.hour_3_start},
            {"time": 12, "price": price_action.hour_3_end},
            {"time": 12, "price": price_action.hour_4_start},
            {"time": 1, "price": price_action.hour_4_end},
            {"time": 1, "price": price_action.hour_5_start},
            {"time": 2, "price": price_action.hour_5_end},
            {"time": 2, "price": price_action.hour_6_start},
            {"time": 3, "price": price_action.hour_6_end},
            {"time": 3, "price": price_action.hour_7_start},
            {"time": 4, "price": price_action.hour_7_end},
        ]
        return list(filter(lambda x: x["price"] != 0, hourly_prices))

    @staticmethod
    def get_starting_price_and_time(price_action):
        filtered_prices = ShortlistUtils.get_non_zero_hourly_prices(price_action)
        return f"{filtered_prices[0]['price']} ({filtered_prices[0]['time']})"

    @staticmethod
    def get_closing_price_and_time(price_action):
        filtered_prices = ShortlistUtils.get_non_zero_hourly_prices(price_action)
        return f"{filtered_prices[-1]['price']} ({filtered_prices[-1]['time']})"

    @staticmethod
    def get_average_gain(stock):
        day_one_filtered_prices = ShortlistUtils.get_non_zero_hourly_prices(stock.price_actions[2])
        day_two_filtered_prices = ShortlistUtils.get_non_zero_hourly_prices(stock.price_actions[1])
        day_three_filtered_prices = ShortlistUtils.get_non_zero_hourly_prices(stock.price_actions[0])
        day_one_gain = day_one_filtered_prices[-1]["price"] - day_one_filtered_prices[0]["price"]
        day_two_gain = day_two_filtered_prices[-1]["price"] - day_two_filtered_prices[0]["price"]
        day_three_gain = day_three_filtered_prices[-1]["price"] - day_three_filtered_prices[0]["price"]
        average = (day_one_gain + day_two_gain + day_three_gain) / 3
        return round(average, 2)

    @staticmethod
    def get_profit_percentage(stock):
        day_one_filtered_prices = ShortlistUtils.get_non_zero_hourly_prices(stock.price_actions[2])
        day_two_filtered_prices = ShortlistUtils.get_non_zero_hourly_prices(stock.price_actions[1])
        day_three_filtered_prices = ShortlistUtils.get_non_zero_hourly_prices(stock.price_actions[0])
        d1_profit_percentage = ((day_one_filtered_prices[-1]["price"] - day_one_filtered_prices[0]["price"])/day_one_filtered_prices[0]["price"]) * 100
        d2_profit_percentage = ((day_two_filtered_prices[-1]["price"] - day_two_filtered_prices[0]["price"])/day_two_filtered_prices[0]["price"]) * 100
        d3_profit_percentage = ((day_three_filtered_prices[-1]["price"] - day_three_filtered_prices[0]["price"])/day_three_filtered_prices[0]["price"]) * 100
        average = (d1_profit_percentage + d2_profit_percentage + d3_profit_percentage) / 3
        return round(average, 2)

    @staticmethod
    def get_buy_price(stock):
        day_three_filtered_prices = ShortlistUtils.get_non_zero_hourly_prices(stock.price_actions[0])
        return day_three_filtered_prices[-1]["price"]

    @staticmethod
    def get_sell_price(stock):
        return ShortlistUtils.get_buy_price(stock) + ShortlistUtils.get_average_gain(stock)

    @staticmethod
    def get_stop_loss_price(stock):
        return ShortlistUtils.get_buy_price(stock) - round((ShortlistUtils.get_average_gain(stock) / 3), 2)

    @staticmethod
    def get_profit_forecast(stock):
        return round(((ShortlistUtils.get_sell_price(stock) - ShortlistUtils.get_buy_price(stock))/ShortlistUtils.get_buy_price(stock)) * 100, 2)
