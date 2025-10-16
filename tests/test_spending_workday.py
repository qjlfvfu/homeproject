import numpy as np
import pandas as pd
import pytest

from src.utils import spending_by_workday


class TestSpendingByWorkday:

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми данными"""
        dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
        np.random.seed(42)

        data = []
        for date in dates:
            # В рабочие дни траты больше
            is_weekend = date.dayofweek >= 5
            base_amount = 1000 if is_weekend else 2000
            amount = np.random.normal(base_amount, 500)

            data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "amount": max(amount, 0),  # Отрицательных трат не бывает
                }
            )

        return pd.DataFrame(data)

    def test_basic_functionality(self, sample_transactions):
        """Тест базовой функциональности"""
        result = spending_by_workday(sample_transactions, "2024-03-31")

        assert not result.empty
        assert len(result) == 2  # рабочий и выходной
        assert set(result["day_type"].values) == {"рабочий", "выходной"}
        assert all(result["avg_spending"] > 0)

    def test_without_date_parameter(self, sample_transactions):
        """Тест без передачи даты"""
        result = spending_by_workday(sample_transactions)
        assert not result.empty

    def test_empty_transactions(self):
        """Тест с пустыми транзакциями"""
        empty_df = pd.DataFrame(columns=["date", "amount"])
        result = spending_by_workday(empty_df, "2024-03-31")
        assert len(result) == 2
        assert all(result["avg_spending"] == 0)

    def test_missing_columns(self):
        """Тест с отсутствующими колонками"""
        invalid_df = pd.DataFrame({"wrong_col": [1, 2, 3]})
        with pytest.raises(ValueError):
            spending_by_workday(invalid_df, "2024-03-31")

    def test_specific_date_range(self, sample_transactions):
        """Тест с конкретным диапазоном дат"""
        result = spending_by_workday(sample_transactions, "2024-01-15")
        # Проверяем что период корректный (3 месяца назад от 15 января)
        assert "2024-01-15" in result["analysis_period"].iloc[0]


# Пример использования
if __name__ == "__main__":
    # Создаем тестовые данные
    test_dates = pd.date_range("2023-12-01", "2024-03-31", freq="D")
    test_data = []

    for date in test_dates:
        is_weekend = date.dayofweek >= 5
        base_amount = 800 if is_weekend else 1500
        amount = np.random.normal(base_amount, 300)

        test_data.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "amount": max(amount, 100),
                "description": f"Transaction {date.strftime('%Y-%m-%d')}",
            }
        )

    test_df = pd.DataFrame(test_data)

    # Тестируем функцию
    print("=== Тест с передачей даты ===")
    result_with_date = spending_by_workday(test_df, "2024-03-31")
    print(result_with_date)
    print()

    print("=== Тест без передачи даты ===")
    result_without_date = spending_by_workday(test_df)
    print(result_without_date)
