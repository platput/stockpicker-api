class Constants:
    """
    Constants class
    """
    # General
    TIME_PERIOD = "time_period"
    STARTING_PRICE = "starting_price"
    ENDING_PRICE = "ending_price"
    STOCK_NAME = "stock_name"
    STOCK_DETAILS = "stock_details"
    DATE = "date"
    PRICE_ACTION = "price_action"
    TIME_ZONE = 'Asia/Kolkata'
    STOCK_DETAILS_URL = "stock_details_url"
    SECTOR_NAME = "sector_name"
    SECTOR_URL = "sector_url"

    # BS4 Specific
    USER_AGENT = {'User-Agent': 'Mozilla/5.0'}
    HTML_PARSER = "html.parser"

    # Time Periods
    NINE_TO_TEN = "9_10"
    TEN_TO_ELEVEN = "10_11"
    ELEVEN_TO_TWELVE = "11_12"
    TWELVE_TO_THIRTEEN = "12_13"
    THIRTEEN_TO_FOURTEEN = "13_14"
    FOURTEEN_TO_FIFTEEN = "14_15"
    FIFTEEN_TO_SIXTEEN = "15_16"

    # Zerodha specific
    GOOGLE_DOC_CSV_EXPORT_READY_URL = "https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={sheet_id}"
    # Current URL: https://docs.google.com/spreadsheets/d/1ZTyh6GiHTwA1d-ApYdn5iCmRiBLZoAtwigS7VyLUk_Y/edit#gid=0
    # DATE: 18/03/2022
    DOC_ID = "1ZTyh6GiHTwA1d-ApYdn5iCmRiBLZoAtwigS7VyLUk_Y"
    SHEET_ID = 0

    # Memcache
    SECTORIAL_INDICES_KEY = "sectorial_indices"
