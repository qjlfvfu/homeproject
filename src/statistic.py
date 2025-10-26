from typing import Dict, List


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
        card_number = transaction.get("card_number", "")
        amount = transaction.get("amount", 0)

        if not card_number:
            continue

        last_digits = card_number[-4:]

        if last_digits not in cards_stats:
            cards_stats[last_digits] = {
                "last_digits": last_digits,
                "total_spent": 0,
                "cashback": 0,
            }

        # Учитываем только расходы (положительные суммы)
        if amount > 0:
            cards_stats[last_digits]["total_spent"] += amount
            cards_stats[last_digits]["cashback"] = (
                cards_stats[last_digits]["total_spent"] / 100
            )

    return list(cards_stats.values())
