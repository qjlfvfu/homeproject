import json
from _datetime import datetime
import logging
from typing import List,Any,Dict
import os


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
        with open(json_file, 'r', encoding='utf-8') as file:
            transactions = json.load(file)

        results = []
        query_lower = query.lower()

        for transaction in transactions:
            description = transaction.get('description', '').lower()
            category = transaction.get('category', '').lower()

            if query_lower in description or query_lower in category:
                results.append(transaction)

        return {
            "query": query,
            "found": len(results),
            "results": results
        }

    except Exception as e:
        return {
            "error": str(e),
            "results": []
        }

    except FileNotFoundError:
        logger.error('Файл не найден!!!💥')
        return {
            "status": "error",
            "message": f"Файл {json_file} не найден",
            "results": []
        }
    except json.JSONDecodeError:
        logger.error('Файл не прочитан!!!💥')
        return {
            "status": "error",
            "message": "Ошибка чтения JSON файла",
            "results": []
        }
    except Exception as e:
        logger.error('Ошибка поиска по файлу💥')
        return {
            "status": "error",
            "message": f"Ошибка при поиске: {str(e)}",
            "results": []
        }