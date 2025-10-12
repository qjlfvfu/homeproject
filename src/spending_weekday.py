import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """
    Рассчитывает средние траты по дням недели за последние три месяца.

    Args:
        transactions: Датафрейм с транзакциями, должен содержать колонки:
                     'date' (дата транзакции), 'amount' (сумма транзакции)
        date: Опциональная дата в формате 'YYYY-MM-DD'. Если не передана,
              используется текущая дата.

    Returns:
        pd.DataFrame: Датафрейм со средними тратами по дням недели
    """
    try:
        # Определяем конечную дату (переданная или текущая)
        if date is None:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(date, '%Y-%m-%d').date()

        # Вычисляем начальную дату (3 месяца назад)
        start_date = end_date - timedelta(days=90)

        logger.info(f"Анализ трат по дням недели за период с {start_date} по {end_date}")

        # Проверяем наличие необходимых колонок
        required_columns = ['date', 'amount']
        if not all(col in transactions.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in transactions.columns]
            raise ValueError(f"Отсутствуют необходимые колонки: {missing_cols}")

        # Преобразуем дату в datetime и фильтруем по периоду
        transactions_copy = transactions.copy()
        transactions_copy['date'] = pd.to_datetime(transactions_copy['date']).dt.date

        # Фильтруем транзакции за последние 3 месяца
        mask = (transactions_copy['date'] >= start_date) & (transactions_copy['date'] <= end_date)
        filtered_transactions = transactions_copy.loc[mask]

        if filtered_transactions.empty:
            logger.warning("Нет транзакций за указанный период")
            return create_empty_weekday_result(start_date, end_date)

        # Добавляем день недели (0=понедельник, 6=воскресенье)
        filtered_transactions['day_of_week'] = pd.to_datetime(
            filtered_transactions['date']
        ).dt.dayofweek

        # Добавляем название дня недели
        days_map = {
            0: 'понедельник',
            1: 'вторник',
            2: 'среда',
            3: 'четверг',
            4: 'пятница',
            5: 'суббота',
            6: 'воскресенье'
        }
        filtered_transactions['weekday_name'] = filtered_transactions['day_of_week'].map(days_map)

        # Группируем по дню недели и считаем статистику
        result = filtered_transactions.groupby(['day_of_week', 'weekday_name']).agg({
            'amount': ['mean', 'sum', 'count', 'std'],
            'date': 'nunique'
        }).round(2)

        # Выравниваем колонки
        result.columns = ['avg_spending', 'total_spending', 'transaction_count', 'std_spending', 'unique_days']

        # Сбрасываем индекс для красивого вывода
        result = result.reset_index()

        # Сортируем по дню недели (понедельник - воскресенье)
        result = result.sort_values('day_of_week')

        # Добавляем информацию о периоде
        result['analysis_period'] = f"{start_date} - {end_date}"

        # Вычисляем медиану трат
        median_by_day = filtered_transactions.groupby('day_of_week')['amount'].median().round(2)
        result['median_spending'] = result['day_of_week'].map(median_by_day)

        logger.info(f"Проанализировано {len(filtered_transactions)} транзакций")
        logger.info(f"Уникальных дней: {result['unique_days'].sum()}")

        return result[['day_of_week', 'weekday_name', 'avg_spending', 'median_spending',
                       'std_spending', 'total_spending', 'transaction_count',
                       'unique_days', 'analysis_period']]

    except Exception as e:
        logger.error(f"Ошибка при расчете трат по дням недели: {str(e)}")
        raise


def create_empty_weekday_result(start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
    """Создает пустой результат с правильной структурой"""
    days_data = []
    days_map = {
        0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг',
        4: 'пятница', 5: 'суббота', 6: 'воскресенье'
    }

    for day_num, day_name in days_map.items():
        days_data.append({
            'day_of_week': day_num,
            'weekday_name': day_name,
            'avg_spending': 0,
            'median_spending': 0,
            'std_spending': 0,
            'total_spending': 0,
            'transaction_count': 0,
            'unique_days': 0,
            'analysis_period': f"{start_date} - {end_date}"
        })

    return pd.DataFrame(days_data)