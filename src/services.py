import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Callable
from functools import reduce
from operator import itemgetter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "services.log")
logger = logging.getLogger("services")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Типы для аннотаций
Transaction = Dict[str, Any]
CashbackAnalysis = Dict[str, float]


# ==================== ВЫГОДНЫЕ КАТЕГОРИИ ПОВЫШЕННОГО КЕШБЭКА ====================

def filter_transactions_by_date(transactions: List[Transaction],
                                year: int,
                                month: int) -> List[Transaction]:
    """
    Фильтрует транзакции по году и месяцу.

    Args:
        transactions: Список транзакций
        year: Год для фильтрации
        month: Месяц для фильтрации

    Returns:
        List[Transaction]: Отфильтрованные транзакции
    """

    def is_target_month(transaction: Transaction) -> bool:
        try:
            # Парсим дату из формата "DD.MM.YYYY"
            trans_date = datetime.strptime(transaction['date'], '%d.%m.%Y')
            return trans_date.year == year and trans_date.month == month
        except (KeyError, ValueError):
            return False

    return list(filter(is_target_month, transactions))


def calculate_category_cashback(transactions: List[Transaction]) -> CashbackAnalysis:
    """
    Рассчитывает кешбэк по категориям.

    Args:
        transactions: Список транзакций

    Returns:
        CashbackAnalysis: Анализ кешбэка по категориям
    """

    def process_transaction(acc: Dict[str, float], transaction: Transaction) -> Dict[str, float]:
        category = transaction.get('category', 'Неизвестно')
        amount = transaction.get('amount', 0)

        # Считаем кешбэк только для расходов (положительные суммы)
        if amount > 0:
            cashback = amount * 0.01  # 1% кешбэк
            acc[category] = acc.get(category, 0) + cashback

        return acc

    return reduce(process_transaction, transactions, {})


def profitable_cashback_categories(data: List[Transaction],
                                   year: int,
                                   month: int) -> str:
    """
    Анализ выгодных категорий повышенного кешбэка.

    Args:
        data: Данные с транзакциями
        year: Год анализа
        month: Месяц анализа

    Returns:
        str: JSON с анализом кешбэка по категориям
    """
    try:
        # Функциональная цепочка обработки
        filtered_transactions = filter_transactions_by_date(data, year, month)
        cashback_analysis = calculate_category_cashback(filtered_transactions)

        # Округляем значения до 2 знаков после запятой
        rounded_analysis = {k: round(v, 2) for k, v in cashback_analysis.items()}

        logger.info(f"Анализ кешбэка завершен для {year}-{month}: {len(rounded_analysis)} категорий")
        return json.dumps(rounded_analysis, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка анализа кешбэка: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== ИНВЕСТКОПИЛКА ====================

def filter_transactions_by_month(transactions: List[Transaction], target_month: str) -> List[Transaction]:
    """
    Фильтрует транзакции по целевому месяцу.

    Args:
        transactions: Список транзакций
        target_month: Месяц в формате 'YYYY-MM'

    Returns:
        List[Transaction]: Отфильтрованные транзакции
    """

    def is_target_month_transaction(transaction: Transaction) -> bool:
        try:
            # Парсим дату из разных возможных форматов
            transaction_date = transaction.get("date", "")

            # Пробуем разные форматы дат
            try:
                trans_date = datetime.strptime(transaction_date, "%Y-%m-%d")
            except ValueError:
                try:
                    trans_date = datetime.strptime(transaction_date, "%d.%m.%Y")
                except ValueError:
                    return False

            target_date = datetime.strptime(target_month, "%Y-%m")
            return trans_date.year == target_date.year and trans_date.month == target_date.month

        except (ValueError, TypeError):
            return False

    return list(filter(is_target_month_transaction, transactions))


def calculate_investment_amount(transactions: List[Transaction], limit: int) -> float:
    """
    Рассчитывает сумму для инвесткопилки.

    Args:
        transactions: Список транзакций
        limit: Предел округления

    Returns:
        float: Сумма для копилки
    """

    def process_investment(acc: float, transaction: Transaction) -> float:
        amount = transaction.get("amount", 0)

        # Округляем только расходы (положительные суммы)
        if amount > 0:
            rounded_amount = ((amount + limit - 1) // limit) * limit  # Округление вверх
            difference = rounded_amount - amount
            if difference > 0:
                return acc + difference

        return acc

    return reduce(process_investment, transactions, 0.0)


def investment_bank(month: str, transactions: List[Transaction], limit: int) -> float:
    """
    Рассчитывает сумму для откладывания в «Инвесткопилку» за указанный месяц.

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций
        limit: Предел для округления сумм операций (10, 50, 100)

    Returns:
        float: Сумма, которую удалось бы отложить в «Инвесткопилку»
    """
    try:
        if limit not in [10, 50, 100]:
            logger.warning(f"Некорректный лимит округления: {limit}")
            return 0.0

        # Функциональная цепочка обработки
        filtered_transactions = filter_transactions_by_month(transactions, month)
        total_investment = calculate_investment_amount(filtered_transactions, limit)

        logger.info(f"Расчет инвесткопилки для {month} с лимитом {limit}: {total_investment:.2f} руб.")
        return round(total_investment, 2)

    except Exception as e:
        logger.error(f"Ошибка расчета инвесткопилки: {e}")
        return 0.0


# ==================== ПРОСТОЙ ПОИСК ====================

def simple_search(query: str, transactions: List[Transaction]) -> str:
    """
    Простой поиск транзакций по запросу в описании или категории.

    Args:
        query: Строка для поиска
        transactions: Список транзакций

    Returns:
        str: JSON с найденными транзакциями
    """
    try:
        query_lower = query.lower()

        def matches_query(transaction: Transaction) -> bool:
            description = transaction.get("description", "").lower()
            category = transaction.get("category", "").lower()
            return query_lower in description or query_lower in category

        results = list(filter(matches_query, transactions))

        response = {
            "query": query,
            "found": len(results),
            "results": results
        }

        logger.info(f"Поиск '{query}': найдено {len(results)} транзакций")
        return json.dumps(response, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка поиска: {e}")
        return json.dumps({"error": str(e), "results": []}, ensure_ascii=False)


# ==================== ПОИСК ПО ТЕЛЕФОННЫМ НОМЕРАМ ====================

def extract_phone_numbers(text: str) -> List[str]:
    """
    Извлекает телефонные номера из текста.

    Args:
        text: Текст для анализа

    Returns:
        List[str]: Найденные телефонные номера
    """
    # Регулярное выражение для российских номеров телефонов
    phone_pattern = r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
    return re.findall(phone_pattern, text)


def has_phone_number(transaction: Transaction) -> bool:
    """
    Проверяет, содержит ли транзакция телефонный номер.

    Args:
        transaction: Транзакция для проверки

    Returns:
        bool: True если содержит номер телефона
    """
    description = transaction.get("description", "")
    return len(extract_phone_numbers(description)) > 0


def search_phone_transactions(transactions: List[Transaction]) -> str:
    """
    Поиск транзакций, содержащих телефонные номера.

    Args:
        transactions: Список транзакций

    Returns:
        str: JSON с найденными транзакциями
    """
    try:
        results = list(filter(has_phone_number, transactions))

        # Добавляем найденные номера телефонов в результат
        enriched_results = []
        for transaction in results:
            enriched_transaction = transaction.copy()
            enriched_transaction["phone_numbers"] = extract_phone_numbers(transaction.get("description", ""))
            enriched_results.append(enriched_transaction)

        response = {
            "search_type": "phone_numbers",
            "found": len(results),
            "results": enriched_results
        }

        logger.info(f"Поиск телефонных номеров: найдено {len(results)} транзакций")
        return json.dumps(response, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка поиска телефонных номеров: {e}")
        return json.dumps({"error": str(e), "results": []}, ensure_ascii=False)


# ==================== ПОИСК ПЕРЕВОДОВ ФИЗИЧЕСКИМ ЛИЦАМ ====================

def is_person_transfer(transaction: Transaction) -> bool:
    """
    Проверяет, является ли транзакция переводом физическому лицу.

    Args:
        transaction: Транзакция для проверки

    Returns:
        bool: True если это перевод физлицу
    """
    category = transaction.get("category", "")
    description = transaction.get("description", "")

    # Проверяем категорию
    if category != "Переводы":
        return False

    # Проверяем описание на наличие имени и фамилии с точкой
    # Паттерн: "Имя Ф." где Ф - первая буква фамилии
    name_pattern = r'[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.'
    return re.search(name_pattern, description) is not None


def search_person_transfers(transactions: List[Transaction]) -> str:
    """
    Поиск переводов физическим лицам.

    Args:
        transactions: Список транзакций

    Returns:
        str: JSON с найденными транзакциями
    """
    try:
        results = list(filter(is_person_transfer, transactions))

        response = {
            "search_type": "person_transfers",
            "found": len(results),
            "results": results
        }

        logger.info(f"Поиск переводов физлицам: найдено {len(results)} транзакций")
        return json.dumps(response, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Ошибка поиска переводов физлицам: {e}")
        return json.dumps({"error": str(e), "results": []}, ensure_ascii=False)


# ==================== УТИЛИТЫ ====================

def load_transactions_from_file(json_file: str) -> List[Transaction]:
    """
    Загружает транзакции из JSON файла.

    Args:
        json_file: Путь к JSON файлу

    Returns:
        List[Transaction]: Список транзакций
    """
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Файл не найден: {json_file}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Ошибка чтения JSON файла: {json_file}")
        return []
    except Exception as e:
        logger.error(f"Ошибка загрузки транзакций: {e}")
        return []


# Пример использования всех сервисов
if __name__ == "__main__":
    # Загрузка тестовых данных
    transactions = load_transactions_from_file("data/transactions.json")

    if transactions:
        print("=== ВЫГОДНЫЕ КАТЕГОРИИ КЕШБЭКА ===")
        cashback_result = profitable_cashback_categories(transactions, 2024, 1)
        print(cashback_result)

        print("\n=== ИНВЕСТКОПИЛКА ===")
        investment = investment_bank("2024-01", transactions, 50)
        print(f"Сумма для копилки: {investment} руб.")

        print("\n=== ПРОСТОЙ ПОИСК ===")
        search_result = simple_search("кофе", transactions)
        print(search_result)

        print("\n=== ПОИСК ТЕЛЕФОННЫХ НОМЕРОВ ===")
        phones_result = search_phone_transactions(transactions)
        print(phones_result)

        print("\n=== ПОИСК ПЕРЕВОДОВ ФИЗЛИЦАМ ===")
        transfers_result = search_person_transfers(transactions)
        print(transfers_result)