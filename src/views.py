import logging
import os
from typing import Any, Dict, List

import requests
from _datetime import date, datetime, timedelta
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_fixed

from src.utils.welcome import format_date
from tests.confest import DEMO_STOCK_PRICES

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


@retry(stop=stop_after_attempt(4), wait=wait_fixed(2))
def currency_analys(user_settings: List[Dict[str, Any]], end_date: str) -> Any:
    """
    Анализ курсов валют за указанный период

    Args:
        start_date: Начальная дата в формате YYYY-MM-DD
        user_settings: Настройки пользователя
        end_date:  Конечная дата в формате YYYY-MM-DD

    Returns:
        Результат анализа курсов валют

    """
    if end_date is None:
        end_date = date.today().strftime("%Y-%m-%d")
    today = date.today()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    url = f"https://api.apilayer.com/currency_data/timeframe?start_date={start_date}&end_date={end_date}"

    payload = {}
    headers = {"apikey": "RLFkPcvU6w1MZKhPv39bkeW2I7SQ0zRX"}

    try:
        response = requests.request(
            "GET", url, headers=headers, data=payload, timeout=10
        )
        response.raise_for_status()

        # Исправляем обработку ответа
        result = response.json()

        if result.get("success", False):
            # Возвращаем данные, а не float
            return result
        else:
            error_info = result.get("error", {}).get("info", "Unknown error")
            print(f"Ошибка API: {error_info}")
            # Возвращаем пустой результат или обрабатываем ошибку
            return {"error": error_info}

    except RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return {"error": str(e)}


def get_top_transactions(transactions_data: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Возвращает топ-N транзакций по сумме платежа.

    Args:
        transactions_data: Список транзакций
        top_n: Количество топовых транзакций

    Returns:
        List[Dict]: Топовые транзакции
    """
    # Фильтруем только расходы (положительные суммы)
    expenses = [t for t in transactions_data if t.get("amount", 0) > 0]

    # Сортируем по сумме (по убыванию) и берем топ-N
    sorted_transactions = sorted(
        expenses, key=lambda x: x.get("amount", 0), reverse=True
    )
    top_transactions = sorted_transactions[:top_n]

    # Форматируем вывод
    formatted_transactions = []
    for transaction in top_transactions:
        formatted_transactions.append(
            {
                "date": format_date(transaction.get("date", "")),
                "amount": round(transaction.get("amount", 0), 2),
                "category": transaction.get("category", "Неизвестно"),
                "description": transaction.get("description", ""),
            }
        )

    return formatted_transactions


def get_currency_rates(api_key: str) -> None | list[Any] | str:
    """
    Получает актуальные курсы валют через API.

    Args:
        api_key: API ключ для currency_data API

    Returns:
        List[Dict]: Курсы валют
    """
    try:
        # Получаем даты для последних доступных данных
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        url = f"https://api.apilayer.com/currency_data/timeframe?start_date={start_date}&end_date={end_date}"

        headers = {"apikey": api_key}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Извлекаем последние доступные курсы
            if data.get("success", False) and data.get("quotes"):
                # Берем последнюю дату из доступных
                latest_date = sorted(data["quotes"].keys())[-1]
                latest_rates = data["quotes"][latest_date]

                currency_rates = []

                # Преобразуем формат валют из USDUSD, USDEUR в USD, EUR
                for currency_pair, rate in latest_rates.items():
                    if currency_pair.startswith("USD"):
                        currency = currency_pair[3:]  # Убираем 'USD' из начала
                        currency_rates.append(
                            {"currency": currency, "rate": round(rate, 2)}
                        )

                # Добавляем USD как базовую валюту
                currency_rates.insert(0, {"currency": "USD", "rate": 1.0})

                return currency_rates[:3]  # Возвращаем топ-3 валюты

        # Если API не сработало, возвращаем демо-данные
        print(f"API request failed. Status: {response.status_code}")
        return "Error"

    except Exception as e:
        print(f"Error fetching currency rates: {e}")


def get_stock_prices_from_yahoo() -> List[Dict]:
    """
    Получает цены акций через Yahoo Finance API.
    """
    try:
        stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        stock_prices = []

        for stock in stocks:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if "chart" in data and "result" in data["chart"]:
                    price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
                    stock_prices.append({"stock": stock, "price": round(price, 2)})

        return stock_prices if stock_prices else DEMO_STOCK_PRICES()

    except Exception as e:
        print(f"Error fetching from Yahoo: {e}")
        return DEMO_STOCK_PRICES()
