import json
import os

import pandas as pd


def create_test_files():
    """Создает тестовые файлы с данными"""

    # Данные для тестов
    test_data = [
        {
            "date": "2024-01-15",
            "amount": 100.50,
            "currency": "USD",
            "description": "Coffee shop purchase",
            "state": "EXECUTED",
        },
        {
            "date": "2024-01-16",
            "amount": 2500.00,
            "currency": "RUB",
            "description": "Payment for services",
            "state": "EXECUTED",
        },
        {
            "date": "2024-01-17",
            "amount": 50.00,
            "currency": "EUR",
            "description": "Coffee with friends",
            "state": "PENDING",
        },
        {
            "date": "2024-01-18",
            "amount": 150.75,
            "currency": "USD",
            "description": "Restaurant dinner",
            "state": "CANCELED",
        },
    ]

    # Создаем CSV файл
    df = pd.DataFrame(test_data)
    df.to_csv("operation.csv", index=False, encoding="utf-8")
    print("✓ Создан файл operation.csv")

    # Создаем Excel файл
    df.to_excel("operation.xlsx", index=False)
    print("✓ Создан файл operation.xlsx")

    # Создаем JSON файл
    with open("user_settings.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    print("✓ Создан файл operation.json")

    print("\nВсе тестовые файлы созданы!")


if __name__ == "__main__":
    create_test_files()
