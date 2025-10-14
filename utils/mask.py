from typing import List


def get_mask_card_number(card_info: str) -> str:
    """Функция, которая возвращает строку после ввода номера карты"""
    parts: List[str] = card_info.split()
    card_number = parts[-1]
    masked_number = f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"
    return masked_number