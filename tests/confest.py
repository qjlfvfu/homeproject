import pytest
import pandas as pd
import json
import sys
import os

print("=== CONFTEST.PY ЗАГРУЖЕН ===")  # Для отладки

# Добавляем путь к src для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Проверяем что пути добавились
print(f"Python path: {sys.path}")

@pytest.fixture
def sample_transactions():
    """Фикстура с примером транзакций"""
    print("=== sample_transactions fixture called ===")
    return [
        {
            "date": "15.01.2024",
            "amount": 1000.0,
            "category": "Продукты",
            "description": "Пятерочка",
            "card_number": "1234567890123456"
        },
        {
            "date": "16.01.2024",
            "amount": 500.0,
            "category": "Кафе",
            "description": "Кофе Starbucks",
            "card_number": "1234567890123456"
        },
        {
            "date": "17.01.2024",
            "amount": 750.0,
            "category": "Транспорт",
            "description": "Такси",
            "card_number": "1234567890123456"
        }
    ]

@pytest.fixture
def sample_dataframe():
    """Фикстура с DataFrame для тестов отчетов"""
    print("=== sample_dataframe fixture called ===")
    data = {
        'date': ['15.01.2024', '16.01.2024', '17.01.2024', '18.01.2024'],
        'amount': [1000, 500, 750, 1200],
        'category': ['Продукты', 'Кафе', 'Транспорт', 'Продукты'],
        'description': ['Пятерочка', 'Starbucks', 'Такси', 'Магнит']
    }
    return pd.DataFrame(data)

@pytest.fixture
def empty_dataframe():
    """Фикстура с пустым DataFrame"""
    return pd.DataFrame(columns=['date', 'amount', 'category', 'description'])

@pytest.fixture
def transactions_with_phones():
    """Фикстура с транзакциями содержащими телефонные номера"""
    return [
        {
            "date": "15.01.2024",
            "amount": 100.0,
            "category": "Связь",
            "description": "Пополнение МТС +7 921 11-22-33"
        }
    ]

@pytest.fixture
def transactions_with_person_transfers():
    """Фикстура с переводами физлицам"""
    return [
        {
            "date": "15.01.2024",
            "amount": 1000.0,
            "category": "Переводы",
            "description": "Валерий А."
        }
    ]