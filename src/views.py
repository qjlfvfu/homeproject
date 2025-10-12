import json
from _datetime import datetime,date
import logging
from typing import List,Any,Dict
import os
import requests
import retry
from requests.exceptions import RequestException, Timeout, ConnectionError
from tenacity import retry, stop_after_attempt, wait_fixed


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "views.log")
logger = logging.getLogger("views")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s")
file_handler.setFormatter(file_formater)
logger.addHandler(file_handler)
API_KEY = os.getenv("API_KEY")


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму для откладывания в «Инвесткопилку» за указанный месяц.

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций с полями 'date' и 'amount'
        limit: Предел для округления сумм операций

    Returns:
        float: Сумма, которую удалось бы отложить в «Инвесткопилку»
    """
    total_investment = 0.0

    for transaction in transactions:
        # Проверяем, что транзакция содержит необходимые поля
        if 'date' not in transaction or 'amount' not in transaction:
            continue

        transaction_date = transaction['date']
        amount = transaction['amount']

        # Проверяем формат даты и что транзакция относится к нужному месяцу
        try:
            # Парсим дату транзакции
            trans_date = datetime.strptime(transaction_date, '%Y-%m-%d')
            # Парсим целевой месяц
            target_month = datetime.strptime(month, '%Y-%m')

            # Проверяем, что транзакция в нужном месяце
            if (trans_date.year == target_month.year and
                    trans_date.month == target_month.month):

                # Округляем сумму до ближайшего кратного limit в большую сторону
                rounded_amount = round(amount / limit) * limit

                # Вычисляем разницу (то, что "откладывается" в копилку)
                difference = rounded_amount - amount

                # Добавляем к общей сумме только если разница положительная
                if difference > 0:
                    total_investment += difference

        except (ValueError, TypeError) as e:
            logger.error('Некорректные данные!!!!')
            # Пропускаем транзакции с некорректными данными
            continue

    return round(total_investment, 2)


@retry(stop=stop_after_attempt(4), wait=wait_fixed(2))
def currency_analys(user_settings: List[Dict[str, Any]],end_date:str) -> Any:
    """
    Анализ курсов валют за указанный период

    Args:
        start_date: Начальная дата в формате YYYY-MM-DD
        user_settings: Настройки пользователя

    Returns:
        Результат анализа курсов валют
    """
    if end_date is None:
        end_date = date.today().strftime("%Y-%m-%d")
    today = date.today()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    url = f"https://api.apilayer.com/currency_data/timeframe?start_date={start_date}&end_date={end_date}"

    payload = {}
    headers = {
        "apikey": "RLFkPcvU6w1MZKhPv39bkeW2I7SQ0zRX"
    }

    try:
        response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()

        # Исправляем обработку ответа
        result = response.json()

        if result.get("success", False):
            # Возвращаем данные, а не float
            return result
        else:
            error_info = result.get('error', {}).get('info', 'Unknown error')
            print(f"Ошибка API: {error_info}")
            # Возвращаем пустой результат или обрабатываем ошибку
            return {"error": error_info}

    except RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return {"error": str(e)}
