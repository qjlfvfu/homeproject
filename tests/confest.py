import pytest

from typing import Any, Dict, List, Tuple
from unittest.mock import patch


@pytest.fixture
def valid_date_formats() -> List[Tuple[str, str]]:
    """Фикстура с валидными датами разных форматов"""
    return [
        ("2023-12-31", "31.12.2023"),
        ("2023-12-31T23:59:59.999", "31.12.2023"),
        ("2023-12-31T14:30:45", "31.12.2023"),
        ("1970-01-01", "01.01.1970"),
        ("2024-02-29T12:00:00.000", "29.02.2024"),
    ]


@pytest.fixture
def edge_case_dates() -> List[Tuple[str, str]]:
    """Фикстура с пограничными случаями дат"""
    return [
        ("2000-01-01T00:00:00.000", "01.01.2000"),
        ("2100-12-31T23:59:59.999", "31.12.2100"),
        ("1900-01-01T12:30:45.123", "01.01.1900"),
    ]


@pytest.fixture
def invalid_dates() -> List[str]:
    """Фикстура с невалидными датами"""
    return ["invalid-date-format", "2023-13-45", "2023/12/31", "31.12.2023", "2023-12-31T25:61:61.999", "", "12345"]


@pytest.fixture
def datetime_formats() -> List[Tuple[str, str]]:
    """Фикстура с разными форматами datetime"""
    return [
        ("2023-01-15T14:30:00.123456", "15.01.2023"),
        ("2023-01-15T14:30:00.123", "15.01.2023"),
        ("2023-01-15T14:30:00", "15.01.2023"),
        ("2023-01-15", "15.01.2023"),
    ]


@pytest.fixture
def test_operations() -> List[Dict[str, Any]]:
    """Фикстура с тестовыми операциями"""
    return [
        {"id": 1, "state": "EXECUTED", "date": "2023-01-01", "amount": 100},
        {"id": 2, "state": "PENDING", "date": "2023-01-02", "amount": 200},
        {"id": 3, "state": "EXECUTED", "date": "2023-01-03", "amount": 300},
        {"id": 4, "state": "CANCELED", "date": "2023-01-04", "amount": 400},
    ]


@pytest.fixture
def account_data() -> List[str]:
    """Фикстура с данными счетов"""
    return ["Счет 1234567890123456", "Счет 9876543210987654", "Visa 1234567812345678"]


@pytest.fixture
def currency_data() -> List[Dict[str, Any]]:
    """Фикстура с данными транзакций"""
    return [
        {"amount": "1300", "from_curr": "RUB", "to_currs": "USD", "date": "2023-02-04"},
        {"amount": "600", "from_curr": "RUB", "to_currs": "USD", "date": "2011-09-11"},
        {"amount": "56473890", "from_curr": "RUB", "to_currs": "USD", "date": "2022-07-04"},
    ]


@pytest.fixture
def mock_requests():
    """Фикстура возвращает мок для requests"""
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def transactions_data() :
    transactions = [
    {'date': '2024-01-15', 'amount': 123.45},
    {'date': '2024-01-20', 'amount': 67.89},
    {'date': '2024-02-01', 'amount': 150.00},
    {'date': '2024-01-25', 'amount': 95.50},
    {'date': '2024-01-30', 'amount': 200.00},
    ]


DEMO_STOCK_PRICES = [
    {
        "stock": "AAPL",
        "price": 150.12
    },
    {
        "stock": "AMZN",
        "price": 3173.18
    },
    {
        "stock": "GOOGL",
        "price": 2742.39
    },
    {
        "stock": "MSFT",
        "price": 296.71
    },
    {
        "stock": "TSLA",
        "price": 1007.08
    }
]