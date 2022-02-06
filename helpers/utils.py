from datetime import datetime


def convert_datetime_string_to_date(datetime_string):
    return datetime.fromisoformat(datetime_string).strftime('%Y-%m-%d')
