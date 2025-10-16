from datetime import datetime
import json
from typing import Optional, List, Dict, Any
from src.utils.statistic import get_card_statistics
from src.utils import get_currency_rates, get_stock_prices_from_yahoo, get_top_transactions
from src.welcome import get_greeting_by_time

def format_currency_rates_for_report(rates_data: Dict) -> List[Dict]:
    """
    Форматирует курсы валют для отчета.

    Args:
        rates_data: Данные о курсах валют

    Returns:
        List[Dict]: Отформатированные курсы валют
    """
    formatted_rates = []

    # Основные валюты для отчета
    target_currencies = ['USD', 'EUR', 'GBP', 'CNY']

    for currency in target_currencies:
        if currency in rates_data:
            formatted_rates.append({
                "currency": currency,
                "rate": round(rates_data[currency], 2)
            })

    # Если нет данных, возвращаем демо-данные
    if not formatted_rates:
        formatted_rates = [
            {"currency": "USD", "rate": 73.21},
            {"currency": "EUR", "rate": 87.08}
        ]

    return formatted_rates


def format_stock_prices_for_report(stocks_data: Dict) -> List[Dict]:
    """
    Форматирует цены акций для отчета.

    Args:
        stocks_data: Данные о ценах акций

    Returns:
        List[Dict]: Отформатированные цены акций
    """
    formatted_stocks = []

    # Основные акции для S&P500
    target_stocks = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']

    for stock in target_stocks:
        if stock in stocks_data:
            formatted_stocks.append({
                "stock": stock,
                "price": round(stocks_data[stock], 2)
            })

    # Если нет данных, возвращаем демо-данные
    if not formatted_stocks:
        formatted_stocks = [
            {"stock": "AAPL", "price": 150.12},
            {"stock": "AMZN", "price": 3173.18},
            {"stock": "GOOGL", "price": 2742.39},
            {"stock": "MSFT", "price": 296.71},
            {"stock": "TSLA", "price": 1007.08}
        ]

    return formatted_stocks


def generate_financial_report(
        time_str: str,
        transactions_data: Optional[List[Dict]] = None,
        currency_api: Optional[str] = None,
        stock_api: Optional[str] = None
) -> Dict[str, Any]:
    """
    Генерирует полный финансовый отчет согласно заданию.

    Args:
        time_str: Время в формате "YYYY-MM-DD HH:MM:SS"
        transactions_data: Данные транзакций
        currency_api: API ключ для курсов валют
        stock_api: API ключ для цен акций

    Returns:
        Dict: Финансовый отчет
    """
    # Получаем приветствие
    greeting = get_greeting_by_time(time_str)

    # Получаем статистику по картам
    cards = get_card_statistics(transactions_data or [])

    # Получаем топ транзакций
    top_transactions = get_top_transactions(transactions_data or [])

    # Получаем курсы валют
    try:
        if currency_api:
            currency_rates_raw = get_currency_rates(api_key=currency_api)
        else:
            currency_rates_raw = get_currency_rates()
        currency_rates = format_currency_rates_for_report(currency_rates_raw)
    except Exception as e:
        print(f"Ошибка получения курсов валют: {e}")
        currency_rates = [
            {"currency": "USD", "rate": 73.21},
            {"currency": "EUR", "rate": 87.08}
        ]

    # Получаем цены акций
    try:
        if stock_api:
            stock_prices_raw = get_stock_prices_from_yahoo(api_key=stock_api)
        else:
            stock_prices_raw = get_stock_prices_from_yahoo()
        stock_prices = format_stock_prices_for_report(stock_prices_raw)
    except Exception as e:
        print(f"Ошибка получения цен акций: {e}")
        stock_prices = [
            {"stock": "AAPL", "price": 150.12},
            {"stock": "AMZN", "price": 3173.18},
            {"stock": "GOOGL", "price": 2742.39},
            {"stock": "MSFT", "price": 296.71},
            {"stock": "TSLA", "price": 1007.08}
        ]

    # Формируем итоговый отчет
    report = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return report


def main(time_str: str, currency_api: str = None, stock_api: str = None) -> str:
    """
    Главная функция согласно заданию.

    Args:
        time_str: Время в формате "YYYY-MM-DD HH:MM:SS"
        currency_api: API для курсов валют
        stock_api: API для цен акций

    Returns:
        str: JSON-строка с финансовым отчетом
    """
    try:
        # Проверяем формат времени
        datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

        # TODO: Заменить на реальные данные транзакций
        # Это пример данных - нужно получить реальные транзакции
        sample_transactions = [
            {
                "card_number": "1234567890125814",
                "amount": 1262.00,
                "date": "2021-12-21",
                "category": "Переводы",
                "description": "Перевод Кредитная карта. ТП 10.2 RUR"
            },
            {
                "card_number": "1234567890127512",
                "amount": 7.94,
                "date": "2021-12-20",
                "category": "Супермаркеты",
                "description": "Лента"
            },
            {
                "card_number": "1234567890125814",
                "amount": 829.00,
                "date": "2021-12-20",
                "category": "Супермаркеты",
                "description": "Лента"
            },
            {
                "card_number": "1234567890125814",
                "amount": 421.00,
                "date": "2021-12-20",
                "category": "Различные товары",
                "description": "Ozon.ru"
            },
            {
                "card_number": "1234567890127512",
                "amount": 14216.42,
                "date": "2021-12-16",
                "category": "ЖКХ",
                "description": "ЖКУ Квартира"
            },
            {
                "card_number": "1234567890125814",
                "amount": 453.00,
                "date": "2021-12-16",
                "category": "Бонусы",
                "description": "Кешбэк за обычные покупки"
            }
        ]

        # Генерируем отчет
        report = generate_financial_report(
            time_str=time_str,
            transactions_data=sample_transactions,  # Заменить на реальные данные
            currency_api=currency_api,
            stock_api=stock_api
        )

        # Возвращаем в формате JSON
        return json.dumps(report, ensure_ascii=False, indent=2)

    except ValueError as e:
        return json.dumps({"error": f"Неверный формат времени: {e}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Ошибка при генерации отчета: {e}"}, ensure_ascii=False)


# Тестирование
if __name__ == "__main__":
    # Тест с разным временем для проверки приветствий
    test_times = [
        "2024-01-15 08:30:00",  # Утро
        "2024-01-15 14:30:00",  # День
        "2024-01-15 19:30:00",  # Вечер
        "2024-01-15 02:30:00",  # Ночь
    ]

    for time_str in test_times:
        print(f"\n=== Тест для времени: {time_str} ===")
        result = main(time_str)
        report_data = json.loads(result)

        if "error" in report_data:
            print(f"Ошибка: {report_data['error']}")
        else:
            print(f"Приветствие: {report_data.get('greeting', 'Неизвестно')}")
            print(f"Количество карт: {len(report_data.get('cards', []))}")
            print(f"Топ транзакций: {len(report_data.get('top_transactions', []))}")
            print(f"Курсы валют: {len(report_data.get('currency_rates', []))}")
            print(f"Акции: {len(report_data.get('stock_prices', []))}")