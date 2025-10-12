import datetime
from datetime import datetime


def greeting(name: str = None) -> str:
    """
    Детальное приветствие с именем

    Args:
        name: Имя пользователя (опционально)

    Returns:
        str: Персонализированное приветствие
    """
    current_hour = datetime.now().hour
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if 0 <= current_hour < 5:
        greet = "Доброй ночи"
        time_period = "ночи"
    elif 5 <= current_hour < 12:
        greet = "Доброе утро"
        time_period = "утра"
    elif 12 <= current_hour < 17:
        greet = "Добрый день"
        time_period = "дня"
    elif 17 <= current_hour < 23:
        greet = "Добрый вечер"
        time_period = "вечера"
    else:
        greet = "Доброй ночи"
        time_period = "ночи"

    if name:
        return f"{greet}, {name}! Сейчас {current_time} ({time_period})."
    else:
        return f"{greet}! Сейчас {current_time} ({time_period})."

