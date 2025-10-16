import datetime
from datetime import datetime


def get_greeting_by_time(time_str: str) -> str:
    """
    Определяет приветствие на основе переданного времени.

    Args:
        time_str: Время в формате "YYYY-MM-DD HH:MM:SS"

    Returns:
        str: Приветствие ("Доброе утро"/"Добрый день"/etc)
    """
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        hour = dt.hour

        if 5 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 17:
            return "Добрый день"
        elif 17 <= hour < 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except Exception:
        return "Добрый день"


def format_date(date_str: str) -> str:
    """
    Форматирует дату из YYYY-MM-DD в DD.MM.YYYY.

    Args:
        date_str: Дата в формате YYYY-MM-DD

    Returns:
        str: Дата в формате DD.MM.YYYY
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d.%m.%Y")
    except:
        return date_str
