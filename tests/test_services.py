import json
import re
from datetime import datetime
from typing import List, Dict, Any


def profitable_cashback_categories(data: List[Dict], year: int, month: int) -> str:
    """
    Анализ выгодных категорий повышенного кешбэка.
    """
    # Простая реализация для тестов
    result = {}
    for transaction in data:
        if transaction.get('amount', 0) > 0:
            category = transaction.get('category', 'Неизвестно')
            cashback = transaction.get('amount', 0) * 0.01
            result[category] = result.get(category, 0) + cashback

    # Округляем значения
    result = {k: round(v, 2) for k, v in result.items()}
    return json.dumps(result, ensure_ascii=False)


def investment_bank(month: str, transactions: List[Dict], limit: int) -> float:
    """
    Рассчитывает сумму для инвесткопилки.
    """
    total = 0.0
    for transaction in transactions:
        amount = transaction.get('amount', 0)
        if amount > 0:
            rounded = ((amount + limit - 1) // limit) * limit
            difference = rounded - amount
            if difference > 0:
                total += difference

    return round(total, 2)
