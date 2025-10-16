import json
import csv
import pandas as pd
from datetime import datetime
from typing import Callable, Any, Optional
import functools
import os


def report_writer(filename: Optional[str] = None):
    """
    Декоратор для записи результатов функций-отчетов в файл.

    Args:
        filename: Имя файла для сохранения. Если не указано, генерируется автоматически.

    Returns:
        Декорированную функцию
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Вызываем оригинальную функцию
            result = func(*args, **kwargs)

            # Генерируем имя файла если не передано
            if filename is None:
                # Формат: report_название_функции_дата_время.расширение
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"report_{func.__name__}_{timestamp}"
            else:
                base_filename = filename

            # Определяем расширение файла и способ сохранения
            file_extension = determine_extension(base_filename)
            final_filename = ensure_extension(base_filename, file_extension)

            try:
                # Сохраняем результат в зависимости от типа данных
                save_result(result, final_filename, file_extension)
                print(f"Отчет сохранен в файл: {final_filename}")

            except Exception as e:
                print(f"Ошибка при сохранении отчета: {e}")
                # Все равно возвращаем результат даже если сохранение не удалось

            return result

        return wrapper

    return decorator


def determine_extension(filename: str) -> str:
    """Определяет расширение файла на основе имени или типа данных по умолчанию."""
    if '.' in filename:
        return filename.split('.')[-1].lower()
    return 'json'  # расширение по умолчанию


def ensure_extension(filename: str, extension: str) -> str:
    """Добавляет расширение к имени файла если его нет."""
    if '.' not in filename:
        return f"{filename}.{extension}"
    return filename


def save_result(result: Any, filename: str, extension: str) -> None:
    """
    Сохраняет результат в файл в зависимости от типа данных и расширения.

    Args:
        result: Данные для сохранения
        filename: Имя файла
        extension: Расширение файла
    """
    # Создаем директорию если её нет
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

    if extension == 'json':
        save_as_json(result, filename)
    elif extension == 'csv':
        save_as_csv(result, filename)
    elif extension in ['xlsx', 'xls']:
        save_as_excel(result, filename)
    elif extension == 'txt':
        save_as_text(result, filename)
    else:
        # По умолчанию сохраняем как JSON
        save_as_json(result, f"{filename}.json")


def save_as_json(result: Any, filename: str) -> None:
    """Сохраняет результат в JSON формате."""
    if isinstance(result, pd.DataFrame):
        # Для DataFrame сохраняем в orient='records' для лучшей читаемости
        result.to_json(filename, orient='records', indent=2, force_ascii=False)
    elif isinstance(result, (dict, list)):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        # Для других типов создаем словарь с результатом
        data = {"result": str(result), "type": type(result).__name__}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def save_as_csv(result: Any, filename: str) -> None:
    """Сохраняет результат в CSV формате."""
    if isinstance(result, pd.DataFrame):
        result.to_csv(filename, index=False, encoding='utf-8')
    elif isinstance(result, list) and all(isinstance(item, dict) for item in result):
        # Список словарей
        if result:
            fieldnames = result[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(result)
    elif isinstance(result, dict):
        # Словарь - сохраняем как одну строку с ключ-значение
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Key', 'Value'])
            for key, value in result.items():
                writer.writerow([key, value])
    else:
        # Для других типов сохраняем как текст
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(result))


def save_as_excel(result: Any, filename: str) -> None:
    """Сохраняет результат в Excel формате."""
    if isinstance(result, pd.DataFrame):
        result.to_excel(filename, index=False)
    elif isinstance(result, dict):
        # Для словаря создаем DataFrame
        if all(isinstance(val, (dict, list)) for val in result.values()):
            # Сложный словарь - сохраняем каждый ключ на отдельном листе
            with pd.ExcelWriter(filename) as writer:
                for sheet_name, data in result.items():
                    if isinstance(data, (pd.DataFrame, list, dict)):
                        df = convert_to_dataframe(data)
                        df.to_excel(writer, sheet_name=str(sheet_name)[:31], index=False)
        else:
            # Простой словарь
            df = pd.DataFrame([result])
            df.to_excel(filename, index=False)
    else:
        # Для других типов создаем простой DataFrame
        df = pd.DataFrame({'result': [str(result)]})
        df.to_excel(filename, index=False)


def save_as_text(result: Any, filename: str) -> None:
    """Сохраняет результат в текстовом формате."""
    with open(filename, 'w', encoding='utf-8') as f:
        if isinstance(result, pd.DataFrame):
            f.write(result.to_string())
        elif isinstance(result, (dict, list)):
            f.write(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            f.write(str(result))


def convert_to_dataframe(data: Any) -> pd.DataFrame:
    """Конвертирует различные типы данных в DataFrame."""
    if isinstance(data, pd.DataFrame):
        return data
    elif isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        return pd.DataFrame([data])
    else:
        return pd.DataFrame({'value': [data]})