import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_fixed

# Настройка логирования
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "views.log")

logger = logging.getLogger("views")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

API_KEY = os.getenv("API_KEY", "RLFkPcvU6w1MZKhPv39bkeW2I7SQ0zRX")


def get_greeting_by_time(time_str: str) -> str:
    """
    Определяет приветствие на основе времени.

    Args:
        time_str: Время в формате "YYYY-MM-DD HH:MM:SS"

    Returns:
        str: Приветствие
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
    except Exception as e:
        logger.error(f"Ошибка определения приветствия: {e}")
        return "Добрый день"


def get_card_statistics(transactions_data: List[Dict]) -> List[Dict]:
    """
    Рассчитывает статистику по картам.

    Args:
        transactions_data: Список транзакций

    Returns:
        List[Dict]: Статистика по картам
    """
    cards_stats = {}

    for transaction in transactions_data:
        card_number = transaction.get('card_number', '')
        amount = transaction.get('amount', 0)

        if not card_number or amount <= 0:
            continue

        last_digits = card_number[-4:]

        if last_digits not in cards_stats:
            cards_stats[last_digits] = {
                'last_digits': last_digits,
                'total_spent': 0,
                'cashback': 0
            }

        cards_stats[last_digits]['total_spent'] += amount
        cards_stats[last_digits]['cashback'] = cards_stats[last_digits]['total_spent'] / 100

    return [
        {
            "last_digits": stats['last_digits'],
            "total_spent": round(stats['total_spent'], 2),
            "cashback": round(stats['cashback'], 2)
        }
        for stats in cards_stats.values()
    ]


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
    expenses = [t for t in transactions_data if t.get('amount', 0) > 0]

    # Сортируем по сумме (по убыванию) и берем топ-N
    sorted_transactions = sorted(expenses, key=lambda x: x.get('amount', 0), reverse=True)
    top_transactions = sorted_transactions[:top_n]

    # Форматируем вывод
    formatted_transactions = []
    for transaction in top_transactions:
        formatted_transactions.append({
            'date': transaction.get('date', ''),
            'amount': round(transaction.get('amount', 0), 2),
            'category': transaction.get('category', 'Неизвестно'),
            'description': transaction.get('description', '')
        })

    return formatted_transactions


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_currency_rates(api_key: str = None) -> List[Dict]:
    """
    Получает актуальные курсы валют через API.

    Args:
        api_key: API ключ для currency_data API

    Returns:
        List[Dict]: Курсы валют в формате [{"currency": "USD", "rate": 73.21}]
    """
    try:
        if not api_key:
            api_key = API_KEY

        # Получаем текущую дату
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        url = f"https://api.apilayer.com/currency_data/timeframe?start_date={start_date}&end_date={end_date}"
        headers = {"apikey": api_key}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("success", False) and data.get("quotes"):
            # Берем последнюю дату из доступных
            latest_date = sorted(data["quotes"].keys())[-1]
            latest_rates = data["quotes"][latest_date]

            currency_rates = []
            target_currencies = ["USDEUR", "USDRUB", "USDGBP", "USDCNY"]  # Основные валюты

            for currency_pair, rate in latest_rates.items():
                if currency_pair in target_currencies:
                    currency = currency_pair[3:]  # Убираем 'USD' из начала
                    currency_rates.append({
                        "currency": currency,
                        "rate": round(rate, 2)
                    })

            # Если получили данные, возвращаем их
            if currency_rates:
                return currency_rates

        logger.warning("Не удалось получить курсы валют из API, используем демо-данные")
        return get_demo_currency_rates()

    except RequestException as e:
        logger.error(f"Ошибка при запросе курсов валют: {e}")
        return get_demo_currency_rates()
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении курсов валют: {e}")
        return get_demo_currency_rates()


def get_demo_currency_rates() -> List[Dict]:
    """Возвращает демо-данные курсов валют"""
    return [
        {"currency": "USD", "rate": 73.21},
        {"currency": "EUR", "rate": 87.08},
        {"currency": "GBP", "rate": 93.45}
    ]


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_stock_prices_from_yahoo() -> List[Dict]:
    """
    Получает цены акций через Yahoo Finance API.

    Returns:
        List[Dict]: Цены акций в формате [{"stock": "AAPL", "price": 150.12}]
    """
    try:
        stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        stock_prices = []

        for stock in stocks:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
                    price = data["chart"]["result"][0]["meta"].get("regularMarketPrice", 0)
                    stock_prices.append({
                        "stock": stock,
                        "price": round(price, 2)
                    })
            else:
                logger.warning(f"Не удалось получить цену акции {stock}")

        # Если получили хотя бы некоторые данные, возвращаем их
        if stock_prices:
            return stock_prices

        logger.warning("Не удалось получить цены акций из API, используем демо-данные")
        return get_demo_stock_prices()

    except RequestException as e:
        logger.error(f"Ошибка при запросе цен акций: {e}")
        return get_demo_stock_prices()
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении цен акций: {e}")
        return get_demo_stock_prices()


def get_demo_stock_prices() -> List[Dict]:
    """Возвращает демо-данные цен акций"""
    return [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08}
    ]


def get_transactions_for_period(transactions_data: List[Dict], time_str: str, period: str = "M") -> List[Dict]:
    """
    Фильтрует транзакции за указанный период.

    Args:
        transactions_data: Список всех транзакций
        time_str: Время в формате "YYYY-MM-DD HH:MM:SS"
        period: Период (W, M, Y, ALL)

    Returns:
        List[Dict]: Отфильтрованные транзакции
    """
    try:
        target_date = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

        if period == "W":  # Неделя
            start_date = target_date - timedelta(days=target_date.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == "M":  # Месяц
            start_date = target_date.replace(day=1)
            end_date = target_date
        elif period == "Y":  # Год
            start_date = target_date.replace(month=1, day=1)
            end_date = target_date
        elif period == "ALL":  # Все данные
            start_date = datetime.min
            end_date = target_date
        else:
            start_date = target_date.replace(day=1)
            end_date = target_date

        filtered_transactions = []
        for transaction in transactions_data:
            try:
                trans_date = datetime.strptime(transaction['date'], "%d.%m.%Y")
                if start_date <= trans_date <= end_date:
                    filtered_transactions.append(transaction)
            except Exception:
                continue

        return filtered_transactions

    except Exception as e:
        logger.error(f"Ошибка фильтрации транзакций: {e}")
        return []


def categorize_transactions(transactions: List[Dict]) -> Dict[str, Dict]:
    """
    Категоризирует транзакции по типам для страницы событий.

    Args:
        transactions: Список транзакций

    Returns:
        Dict: Словарь с расходами и поступлениями
    """
    expenses = {}
    income = {}

    for transaction in transactions:
        amount = transaction.get('amount', 0)
        category = transaction.get('category', 'Неизвестно')

        if amount > 0:  # Расходы
            if category not in expenses:
                expenses[category] = 0
            expenses[category] += amount
        else:  # Поступления
            if category not in income:
                income[category] = 0
            income[category] += abs(amount)

    return {"expenses": expenses, "income": income}


def format_categories_for_report(categories: Dict[str, float], top_n: int = 7) -> List[Dict]:
    """
    Форматирует категории для отчета.

    Args:
        categories: Словарь категорий и сумм
        top_n: Количество топовых категорий

    Returns:
        List[Dict]: Отформатированные категории
    """
    if not categories:
        return []

    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    if len(sorted_categories) <= top_n:
        return [{"category": cat, "amount": round(amount)} for cat, amount in sorted_categories]

    # Берем топ-N и остальное суммируем
    main_categories = [{"category": cat, "amount": round(amount)}
                       for cat, amount in sorted_categories[:top_n - 1]]

    other_amount = sum(amount for _, amount in sorted_categories[top_n - 1:])
    main_categories.append({"category": "Остальное", "amount": round(other_amount)})

    return main_categories


# Главные функции для API endpoints
def generate_main_page_report(time_str: str, transactions_data: List[Dict]) -> Dict[str, Any]:
    """
    Генерация отчета для главной страницы.

    Args:
        time_str: Время в формате "YYYY-MM-DD HH:MM:SS"
        transactions_data: Список транзакций

    Returns:
        Dict: JSON-ответ для главной страницы
    """
    # Фильтруем транзакции за текущий месяц
    filtered_transactions = get_transactions_for_period(transactions_data, time_str, "M")

    report = {
        "greeting": get_greeting_by_time(time_str),
        "cards": get_card_statistics(filtered_transactions),
        "top_transactions": get_top_transactions(filtered_transactions, 5),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices_from_yahoo()
    }

    return report


def generate_events_page_report(time_str: str, transactions_data: List[Dict], period: str = "M") -> Dict[str, Any]:
    """
    Генерация отчета для страницы событий.

    Args:
        time_str: Время в формате "YYYY-MM-DD HH:MM:SS"
        transactions_data: Список транзакций
        period: Период (W, M, Y, ALL)

    Returns:
        Dict: JSON-ответ для страницы событий
    """
    # Фильтруем транзакции за указанный период
    filtered_transactions = get_transactions_for_period(transactions_data, time_str, period)

    # Категоризируем транзакции
    categorized = categorize_transactions(filtered_transactions)

    # Формируем отчет
    report = {
        "expenses": {
            "total_amount": round(sum(categorized["expenses"].values())),
            "main": format_categories_for_report(categorized["expenses"], 7),
            "transfers_and_cash": format_categories_for_report({
                k: v for k, v in categorized["expenses"].items()
                if k in ["Наличные", "Переводы"]
            })
        },
        "income": {
            "total_amount": round(sum(categorized["income"].values())),
            "main": format_categories_for_report(categorized["income"])
        },
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices_from_yahoo()
    }

    return report


# Функции для использования в веб-фреймворке
def main_page_view(time_str: str, transactions_data: List[Dict]) -> str:
    """Веб-вид для главной страницы"""
    report = generate_main_page_report(time_str, transactions_data)
    return json.dumps(report, ensure_ascii=False, indent=2)


def events_page_view(time_str: str, transactions_data: List[Dict], period: str = "M") -> str:
    """Веб-вид для страницы событий"""
    report = generate_events_page_report(time_str, transactions_data, period)
    return json.dumps(report, ensure_ascii=False, indent=2)