import logging
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def spending_by_workday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> pd.DataFrame:
    """
    Рассчитывает средние траты в рабочий и выходной день за последние три месяца.

    Args:
        transactions: Датафрейм с транзакциями, должен содержать колонки:
                     'date' (дата транзакции), 'amount' (сумма транзакции)
        date: Опциональная дата в формате 'YYYY-MM-DD'. Если не передана,
              используется текущая дата.

    Returns:
        pd.DataFrame: Датафрейм со средними тратами по типам дней
    """
    try:
        # Определяем конечную дату (переданная или текущая)
        if date is None:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d").date()

        # Вычисляем начальную дату (3 месяца назад)
        start_date = end_date - timedelta(days=90)

        logger.info(f"Анализ трат за период с {start_date} по {end_date}")

        # Проверяем наличие необходимых колонок
        required_columns = ["date", "amount"]
        if not all(col in transactions.columns for col in required_columns):
            missing_cols = [
                col for col in required_columns if col not in transactions.columns
            ]
            raise ValueError(f"Отсутствуют необходимые колонки: {missing_cols}")

        # Преобразуем дату в datetime и фильтруем по периоду
        transactions_copy = transactions.copy()
        transactions_copy["date"] = pd.to_datetime(transactions_copy["date"]).dt.date

        # Фильтруем транзакции за последние 3 месяца
        mask = (transactions_copy["date"] >= start_date) & (
            transactions_copy["date"] <= end_date
        )
        filtered_transactions = transactions_copy.loc[mask]

        if filtered_transactions.empty:
            logger.warning("Нет транзакций за указанный период")
            return pd.DataFrame(
                {
                    "day_type": ["рабочий", "выходной"],
                    "avg_spending": [0, 0],
                    "transaction_count": [0, 0],
                }
            )

        # Определяем тип дня (рабочий/выходной)
        # 0-4 = понедельник-пятница (рабочие), 5-6 = суббота-воскресенье (выходные)
        filtered_transactions["day_of_week"] = pd.to_datetime(
            filtered_transactions["date"]
        ).dt.dayofweek
        filtered_transactions["day_type"] = np.where(
            filtered_transactions["day_of_week"] < 5, "рабочий", "выходной"
        )

        # Группируем по типу дня и считаем статистику
        result = (
            filtered_transactions.groupby("day_type")
            .agg({"amount": ["mean", "count"], "date": "nunique"})
            .round(2)
        )

        # Выравниваем колонки
        result.columns = ["avg_spending", "transaction_count", "unique_days"]

        # Сбрасываем индекс для красивого вывода
        result = result.reset_index()

        # Добавляем информацию о периоде
        result["analysis_period"] = f"{start_date} - {end_date}"

        logger.info(f"Проанализировано {len(filtered_transactions)} транзакций")
        logger.info(f"Уникальных дней: {result['unique_days'].sum()}")

        return result[
            [
                "day_type",
                "avg_spending",
                "transaction_count",
                "unique_days",
                "analysis_period",
            ]
        ]

    except Exception as e:
        logger.error(f"Ошибка при расчете трат: {str(e)}")
        raise
