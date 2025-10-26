import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Callable, Any
import pandas as pd
import pytest

# Настройка логирования
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "reports.log")

logger = logging.getLogger("reports")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


# ==================== ДЕКОРАТОР ДЛЯ ЗАПИСИ ОТЧЕТОВ ====================

def report_to_file(func: Optional[Callable] = None, *, filename: Optional[str] = None):
    """
    Декоратор для записи результатов отчетов в файл.

    Args:
        func: Декорируемая функция
        filename: Имя файла для сохранения (опционально)
    """

    def decorator(report_func: Callable) -> Callable:
        @wraps(report_func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Выполняем функцию отчета
                result = report_func(*args, **kwargs)

                # Определяем имя файла
                if filename:
                    report_filename = filename
                else:
                    # Генерируем имя файла по умолчанию
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    func_name = report_func.__name__
                    report_filename = f"report_{func_name}_{timestamp}.json"

                # Создаем директорию reports если её нет
                reports_dir = os.path.join(BASE_DIR, "reports")
                os.makedirs(reports_dir, exist_ok=True)
                file_path = os.path.join(reports_dir, report_filename)

                # Сохраняем результат в файл
                if isinstance(result, pd.DataFrame):
                    # Для DataFrame сохраняем в JSON
                    result.to_json(file_path, orient='records', indent=2, force_ascii=False)
                else:
                    # Для других типов данных используем json.dump
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)

                logger.info(f"Отчет сохранен в файл: {file_path}")
                return result

            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")
                # Пробрасываем исключение дальше
                raise

        return wrapper

    # Обработка вызова с параметрами и без
    if func is None:
        return decorator
    else:
        return decorator(func)


# ==================== УТИЛИТНЫЕ ФУНКЦИИ ====================

def parse_date(date_str: Optional[str]) -> datetime:
    """
    Парсит дату из строки или возвращает текущую дату.

    Args:
        date_str: Строка с датой в формате YYYY-MM-DD

    Returns:
        datetime: Объект datetime
    """
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"Некорректный формат даты: {date_str}. Используется текущая дата.")
            return datetime.now()
    else:
        return datetime.now()


def get_last_three_months_range(target_date: datetime) -> tuple:
    """
    Возвращает диапазон дат за последние 3 месяца.

    Args:
        target_date: Целевая дата

    Returns:
        tuple: (start_date, end_date)
    """
    # Начало периода - первый день месяца 3 месяца назад
    start_date = (target_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    start_date = start_date.replace(day=1)

    # Конец периода - переданная дата
    end_date = target_date

    return start_date, end_date


def filter_transactions_by_date(transactions: pd.DataFrame,
                                start_date: datetime,
                                end_date: datetime) -> pd.DataFrame:
    """
    Фильтрует транзакции по диапазону дат.

    Args:
        transactions: DataFrame с транзакциями
        start_date: Начальная дата
        end_date: Конечная дата

    Returns:
        pd.DataFrame: Отфильтрованный DataFrame
    """
    try:
        # Преобразуем столбец с датами в datetime
        transactions_copy = transactions.copy()
        transactions_copy['date'] = pd.to_datetime(transactions_copy['date'], format='%d.%m.%Y', errors='coerce')

        # Фильтруем по диапазону дат
        mask = (transactions_copy['date'] >= start_date) & (transactions_copy['date'] <= end_date)
        return transactions_copy[mask].copy()

    except Exception as e:
        logger.error(f"Ошибка фильтрации транзакций: {e}")
        return pd.DataFrame()


# ==================== ОТЧЕТ: ТРАТЫ ПО КАТЕГОРИИ ====================

@report_to_file
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
    Анализ трат по заданной категории за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями
        category: Название категории для анализа
        date: Опциональная дата в формате YYYY-MM-DD

    Returns:
        pd.DataFrame: Траты по категории с разбивкой по месяцам
    """
    try:
        target_date = parse_date(date)
        start_date, end_date = get_last_three_months_range(target_date)

        logger.info(f"Анализ трат по категории '{category}' за период {start_date.date()} - {end_date.date()}")

        # Фильтруем транзакции по дате
        filtered_df = filter_transactions_by_date(transactions, start_date, end_date)

        if filtered_df.empty:
            logger.warning("Нет данных за указанный период")
            return pd.DataFrame(columns=['month', 'category', 'total_spent'])

        # Фильтруем по категории и положительным суммам (расходы)
        category_df = filtered_df[
            (filtered_df['category'] == category) &
            (filtered_df['amount'] > 0)
            ].copy()

        if category_df.empty:
            logger.warning(f"Нет трат по категории '{category}' за указанный период")
            return pd.DataFrame(columns=['month', 'category', 'total_spent'])

        # Группируем по месяцам и суммируем траты
        category_df['month'] = category_df['date'].dt.to_period('M')
        monthly_spending = category_df.groupby('month').agg({
            'amount': 'sum',
            'category': 'first'
        }).reset_index()

        monthly_spending['month'] = monthly_spending['month'].astype(str)
        monthly_spending.rename(columns={'amount': 'total_spent'}, inplace=True)

        # Добавляем общую сумму
        total = monthly_spending['total_spent'].sum()
        total_row = pd.DataFrame({
            'month': ['Всего'],
            'category': [category],
            'total_spent': [total]
        })

        result_df = pd.concat([monthly_spending, total_row], ignore_index=True)
        logger.info(f"Найдено трат по категории '{category}': {total:.2f} руб.")

        return result_df

    except Exception as e:
        logger.error(f"Ошибка анализа трат по категории: {e}")
        return pd.DataFrame(columns=['month', 'category', 'total_spent'])


# ==================== ОТЧЕТ: ТРАТЫ ПО ДНЯМ НЕДЕЛИ ====================

@report_to_file(filename="weekly_spending_report.json")
def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """
    Анализ средних трат по дням недели за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями
        date: Опциональная дата в формате YYYY-MM-DD

    Returns:
        pd.DataFrame: Средние траты по дням недели
    """
    try:
        target_date = parse_date(date)
        start_date, end_date = get_last_three_months_range(target_date)

        logger.info(f"Анализ трат по дням недели за период {start_date.date()} - {end_date.date()}")

        # Фильтруем транзакции по дате
        filtered_df = filter_transactions_by_date(transactions, start_date, end_date)

        if filtered_df.empty:
            logger.warning("Нет данных за указанный период")
            return pd.DataFrame(columns=['weekday', 'average_spent', 'transaction_count'])

        # Фильтруем только расходы (положительные суммы)
        expenses_df = filtered_df[filtered_df['amount'] > 0].copy()

        if expenses_df.empty:
            logger.warning("Нет трат за указанный период")
            return pd.DataFrame(columns=['weekday', 'average_spent', 'transaction_count'])

        # Добавляем день недели (0 = понедельник, 6 = воскресенье)
        expenses_df['weekday'] = expenses_df['date'].dt.dayofweek

        # Словарь для преобразования номера дня в название
        weekday_names = {
            0: 'Понедельник',
            1: 'Вторник',
            2: 'Среда',
            3: 'Четверг',
            4: 'Пятница',
            5: 'Суббота',
            6: 'Воскресенье'
        }

        # Группируем по дням недели и вычисляем статистику
        weekday_stats = expenses_df.groupby('weekday').agg({
            'amount': ['mean', 'count']
        }).reset_index()

        # Выравниваем мультииндекс
        weekday_stats.columns = ['weekday', 'average_spent', 'transaction_count']

        # Преобразуем номера дней в названия
        weekday_stats['weekday'] = weekday_stats['weekday'].map(weekday_names)

        # Сортируем по порядку дней недели
        weekday_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        weekday_stats['weekday'] = pd.Categorical(weekday_stats['weekday'], categories=weekday_order, ordered=True)
        weekday_stats = weekday_stats.sort_values('weekday').reset_index(drop=True)

        # Округляем значения
        weekday_stats['average_spent'] = weekday_stats['average_spent'].round(2)

        logger.info(f"Проанализировано {len(expenses_df)} транзакций по дням недели")
        return weekday_stats

    except Exception as e:
        logger.error(f"Ошибка анализа трат по дням недели: {e}")
        return pd.DataFrame(columns=['weekday', 'average_spent', 'transaction_count'])


# ==================== ОТЧЕТ: ТРАТЫ В РАБОЧИЙ/ВЫХОДНОЙ ДЕНЬ ====================

@report_to_file
def spending_by_workday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    """
    Анализ средних трат в рабочие и выходные дни за последние три месяца.

    Args:
        transactions: DataFrame с транзакций
        date: Опциональная дата в формате YYYY-MM-DD

    Returns:
        pd.DataFrame: Средние траты в рабочие и выходные дни
    """
    try:
        target_date = parse_date(date)
        start_date, end_date = get_last_three_months_range(target_date)

        logger.info(f"Анализ трат по типам дней за период {start_date.date()} - {end_date.date()}")

        # Фильтруем транзакции по дате
        filtered_df = filter_transactions_by_date(transactions, start_date, end_date)

        if filtered_df.empty:
            logger.warning("Нет данных за указанный период")
            return pd.DataFrame(columns=['day_type', 'average_spent', 'transaction_count'])

        # Фильтруем только расходы (положительные суммы)
        expenses_df = filtered_df[filtered_df['amount'] > 0].copy()

        if expenses_df.empty:
            logger.warning("Нет трат за указанный период")
            return pd.DataFrame(columns=['day_type', 'average_spent', 'transaction_count'])

        # Определяем тип дня (рабочий/выходной)
        # Пн-Пт (0-4) - рабочие, Сб-Вс (5-6) - выходные
        expenses_df['day_type'] = expenses_df['date'].dt.dayofweek.apply(
            lambda x: 'Выходной' if x >= 5 else 'Рабочий'
        )

        # Группируем по типу дня и вычисляем статистику
        workday_stats = expenses_df.groupby('day_type').agg({
            'amount': ['mean', 'count']
        }).reset_index()

        # Выравниваем мультииндекс
        workday_stats.columns = ['day_type', 'average_spent', 'transaction_count']

        # Округляем значения
        workday_stats['average_spent'] = workday_stats['average_spent'].round(2)

        # Добавляем строку с общими показателями
        total_avg = expenses_df['amount'].mean()
        total_count = len(expenses_df)
        total_row = pd.DataFrame({
            'day_type': ['Всего'],
            'average_spent': [round(total_avg, 2)],
            'transaction_count': [total_count]
        })

        result_df = pd.concat([workday_stats, total_row], ignore_index=True)

        logger.info(
            f"Проанализировано {total_count} транзакций: {workday_stats.iloc[0]['transaction_count']} рабочих, {workday_stats.iloc[1]['transaction_count']} выходных")
        return result_df

    except Exception as e:
        logger.error(f"Ошибка анализа трат по типам дней: {e}")
        return pd.DataFrame(columns=['day_type', 'average_spent', 'transaction_count'])


# ==================== ТЕСТИРОВАНИЕ ====================

def create_sample_data() -> pd.DataFrame:
    """
    Создает пример данных для тестирования.

    Returns:
        pd.DataFrame: Пример DataFrame с транзакциями
    """
    data = {
        'date': [
            '15.01.2024', '16.01.2024', '17.01.2024', '18.01.2024', '19.01.2024',
            '20.01.2024', '21.01.2024', '14.12.2023', '15.12.2023', '16.12.2023'
        ],
        'amount': [1000, 500, 750, 1200, 300, 2000, 800, 600, 900, 1100],
        'category': [
            'Продукты', 'Кафе', 'Транспорт', 'Продукты', 'Развлечения',
            'Продукты', 'Кафе', 'Продукты', 'Транспорт', 'Кафе'
        ],
        'description': [
            'Пятерочка', 'Starbucks', 'Такси', 'Магнит', 'Кино',
            'Ашан', 'Кофейня', 'Лента', 'Метро', 'Кофе'
        ]
    }
    return pd.DataFrame(data)


# Пример использования
if __name__ == "__main__":
    # Создаем тестовые данные
    sample_data = create_sample_data()

    print("=== ТРАТЫ ПО КАТЕГОРИИ ===")
    category_report = spending_by_category(sample_data, "Продукты", "2024-01-20")
    print(category_report.to_string())

    print("\n=== ТРАТЫ ПО ДНЯМ НЕДЕЛИ ===")
    weekday_report = spending_by_weekday(sample_data, "2024-01-20")
    print(weekday_report.to_string())

    print("\n=== ТРАТЫ В РАБОЧИЙ/ВЫХОДНОЙ ДЕНЬ ===")
    workday_report = spending_by_workday(sample_data, "2024-01-20")
    print(workday_report.to_string())