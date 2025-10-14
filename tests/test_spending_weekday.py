import pytest
import numpy as np
import pandas as pd
from utils.spending_weekday import spending_by_weekday


class TestSpendingByWeekday:

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми данными"""
        dates = pd.date_range('2024-01-01', '2024-03-31', freq='D')
        np.random.seed(42)

        data = []
        for date in dates:
            # Разные траты по дням недели
            day_of_week = date.dayofweek
            base_amounts = [1000, 1200, 1100, 1300, 1500, 800, 700]  # пн-вс
            base_amount = base_amounts[day_of_week]
            amount = np.random.normal(base_amount, 200)

            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'amount': max(amount, 0)
            })

        return pd.DataFrame(data)

    def test_basic_functionality(self, sample_transactions):
        """Тест базовой функциональности"""
        result = spending_by_weekday(sample_transactions, '2024-03-31')

        assert not result.empty
        assert len(result) == 7  # 7 дней недели
        assert set(result['weekday_name'].values) == {
            'понедельник', 'вторник', 'среда', 'четверг',
            'пятница', 'суббота', 'воскресенье'
        }
        assert all(result['avg_spending'] > 0)
        assert list(result['day_of_week'].values) == [0, 1, 2, 3, 4, 5, 6]  # правильный порядок

    def test_without_date_parameter(self, sample_transactions):
        """Тест без передачи даты"""
        result = spending_by_weekday(sample_transactions)
        assert not result.empty
        assert len(result) == 7

    def test_empty_transactions(self):
        """Тест с пустыми транзакциями"""
        empty_df = pd.DataFrame(columns=['date', 'amount'])
        result = spending_by_weekday(empty_df, '2024-03-31')
        assert len(result) == 7
        assert all(result['avg_spending'] == 0)
        assert all(result['transaction_count'] == 0)

    def test_missing_columns(self):
        """Тест с отсутствующими колонками"""
        invalid_df = pd.DataFrame({'wrong_col': [1, 2, 3]})
        with pytest.raises(ValueError):
            spending_by_weekday(invalid_df, '2024-03-31')

    def test_specific_date_range(self, sample_transactions):
        """Тест с конкретным диапазоном дат"""
        result = spending_by_weekday(sample_transactions, '2024-01-15')
        assert '2024-01-15' in result['analysis_period'].iloc[0]

    def test_weekday_patterns(self, sample_transactions):
        """Тест паттернов по дням недели"""
        result = spending_by_weekday(sample_transactions, '2024-03-31')

        # Проверяем что пятница имеет высокие траты (как в тестовых данных)
        friday_data = result[result['weekday_name'] == 'пятница'].iloc[0]
        sunday_data = result[result['weekday_name'] == 'воскресенье'].iloc[0]

        # В тестовых данных пятница = 1500, воскресенье = 700
        assert friday_data['avg_spending'] > sunday_data['avg_spending']


# Пример использования
if __name__ == "__main__":
    # Создаем тестовые данные с разными паттернами по дням недели
    test_dates = pd.date_range('2023-12-01', '2024-03-31', freq='D')
    test_data = []

    # Базовые траты по дням недели (пн-вс)
    base_amounts = [1200, 1100, 1000, 1300, 2000, 800, 600]

    for date in test_dates:
        day_of_week = date.dayofweek
        base_amount = base_amounts[day_of_week]
        amount = np.random.normal(base_amount, 300)

        test_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': max(amount, 100),
            'description': f"Transaction {date.strftime('%Y-%m-%d')}"
        })

    test_df = pd.DataFrame(test_data)

    print("=== Тест с передачей даты ===")
    result_with_date = spending_by_weekday(test_df, '2024-03-31')
    print(result_with_date.to_string(index=False))
    print()

    print("=== Статистика по дням недели ===")
    for _, row in result_with_date.iterrows():
        print(f"{row['weekday_name']:12}: {row['avg_spending']:8.2f} руб. (медиана: {row['median_spending']:6.2f})")

    print("\n=== Тест без передачи даты ===")
    result_without_date = spending_by_weekday(test_df)
    print(f"Период анализа: {result_without_date['analysis_period'].iloc[0]}")
    print(f"Всего транзакций: {result_without_date['transaction_count'].sum()}")