import json
import logging
import os
from typing import Any, Dict, List

from _datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "services.log")
logger = logging.getLogger("services")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s")
file_handler.setFormatter(file_formater)
logger.addHandler(file_handler)


def finder(query, json_file):
    """
    Поиск транзакций по запросу в описании или категории
    Возвращает JSON с найденными транзакциями
    """
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            transactions = json.load(file)

        results = []
        query_lower = query.lower()

        for transaction in transactions:
            description = transaction.get("description", "").lower()
            category = transaction.get("category", "").lower()

            if query_lower in description or query_lower in category:
                results.append(transaction)

        return {"query": query, "found": len(results), "results": results}

    except Exception as e:
        return {"error": str(e), "results": []}

    except FileNotFoundError:
        logger.error("Файл не найден!!!💥")
        return {
            "status": "error",
            "message": f"Файл {json_file} не найден",
            "results": [],
        }
    except json.JSONDecodeError:
        logger.error("Файл не прочитан!!!💥")
        return {"status": "error", "message": "Ошибка чтения JSON файла", "results": []}
    except Exception as e:
        logger.error("Ошибка поиска по файлу💥")
        return {
            "status": "error",
            "message": f"Ошибка при поиске: {str(e)}",
            "results": [],
        }


def investment_bank(
    month: str, transactions: List[Dict[str, Any]], limit: int
) -> float:
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
        if "date" not in transaction or "amount" not in transaction:
            continue

        transaction_date = transaction["date"]
        amount = transaction["amount"]

        # Проверяем формат даты и что транзакция относится к нужному месяцу
        try:
            # Парсим дату транзакции
            trans_date = datetime.strptime(transaction_date, "%Y-%m-%d")
            # Парсим целевой месяц
            target_month = datetime.strptime(month, "%Y-%m")

            # Проверяем, что транзакция в нужном месяце
            if (
                trans_date.year == target_month.year
                and trans_date.month == target_month.month
            ):

                # Округляем сумму до ближайшего кратного limit в большую сторону
                rounded_amount = round(amount / limit) * limit

                # Вычисляем разницу (то, что "откладывается" в копилку)
                difference = rounded_amount - amount

                # Добавляем к общей сумме только если разница положительная
                if difference > 0:
                    total_investment += difference

        except (ValueError, TypeError):
            logger.error("Некорректные данные!!!!")
            # Пропускаем транзакции с некорректными данными
            continue

    return round(total_investment, 2)


