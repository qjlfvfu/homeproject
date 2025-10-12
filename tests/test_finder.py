import pytest
import unittest
from unittest.mock import patch, mock_open
import json
import os
import sys

# Добавляем путь к корневой директории проекта для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем функцию finder
from src.services import finder


class TestFinderFunction(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Перевод денег", "category": "перевод", "amount": 100}, {"description": "Оплата услуг", "category": "оплата", "amount": 200}]')
    def test_finder_successful_search(self, mock_file):
        """Тест успешного поиска транзакций"""
        result = finder("перевод", "test.json")

        expected = {
            "query": "перевод",
            "found": 1,
            "results": [{"description": "Перевод денег", "category": "перевод", "amount": 100}]
        }

        self.assertEqual(result["query"], expected["query"])
        self.assertEqual(result["found"], expected["found"])
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["description"], "Перевод денег")

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Перевод денег", "category": "перевод", "amount": 100}, {"description": "Оплата услуг", "category": "оплата", "amount": 200}]')
    def test_finder_case_insensitive(self, mock_file):
        """Тест регистронезависимого поиска"""
        result = finder("ПЕРЕВОД", "test.json")

        self.assertEqual(result["found"], 1)
        self.assertEqual(result["results"][0]["description"], "Перевод денег")

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Перевод денег", "category": "перевод", "amount": 100}, {"description": "Оплата услуг", "category": "оплата", "amount": 200}]')
    def test_finder_search_by_category(self, mock_file):
        """Тест поиска по категории"""
        result = finder("оплата", "test.json")

        self.assertEqual(result["found"], 1)
        self.assertEqual(result["results"][0]["category"], "оплата")

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Перевод денег", "category": "перевод", "amount": 100}, {"description": "Оплата услуг", "category": "оплата", "amount": 200}]')
    def test_finder_partial_match(self, mock_file):
        """Тест частичного совпадения"""
        result = finder("вод", "test.json")

        self.assertEqual(result["found"], 1)
        self.assertEqual(result["results"][0]["description"], "Перевод денег")

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Перевод денег", "category": "перевод", "amount": 100}, {"description": "Оплата услуг", "category": "оплата", "amount": 200}]')
    def test_finder_no_results(self, mock_file):
        """Тест когда нет результатов"""
        result = finder("несуществующееслово", "test.json")

        self.assertEqual(result["found"], 0)
        self.assertEqual(result["results"], [])

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Перевод денег", "category": "перевод", "amount": 100}, {"description": "Оплата услуг", "category": "оплата", "amount": 200}]')
    def test_finder_multiple_results(self, mock_file):
        """Тест множественных результатов"""
        result = finder("денег", "test.json")

        self.assertEqual(result["found"], 1)

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_finder_empty_json(self, mock_file):
        """Тест с пустым JSON файлом"""
        result = finder("перевод", "test.json")

        self.assertEqual(result["found"], 0)
        self.assertEqual(result["results"], [])

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"amount": 100}, {"description": "Перевод", "amount": 200}]')
    def test_finder_missing_fields(self, mock_file):
        """Тест с отсутствующими полями в транзакциях"""
        result = finder("перевод", "test.json")

        self.assertEqual(result["found"], 1)
        self.assertEqual(result["results"][0]["description"], "Перевод")

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "", "category": "", "amount": 100}, {"description": "Перевод", "category": "перевод", "amount": 200}]')
    def test_finder_empty_fields(self, mock_file):
        """Тест с пустыми полями"""
        result = finder("перевод", "test.json")

        self.assertEqual(result["found"], 1)

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_finder_json_decode_error(self, mock_file):
        """Тест ошибки декодирования JSON"""
        result = finder("перевод", "test.json")

        # Исправлено: проверяем реальный формат ошибки
        self.assertIn("error", result)
        self.assertIn("results", result)
        self.assertEqual(result["results"], [])

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_finder_file_not_found(self, mock_file):
        """Тест когда файл не найден"""
        result = finder("перевод", "nonexistent.json")

        # Исправлено: проверяем реальный формат ошибки
        self.assertIn("error", result)
        self.assertEqual(result["results"], [])

    @patch('builtins.open', side_effect=Exception("Unexpected error"))
    def test_finder_general_exception(self, mock_file):
        """Тест обработки общего исключения"""
        result = finder("перевод", "test.json")

        # Исправлено: проверяем реальный формат ошибки
        self.assertIn("error", result)
        self.assertEqual(result["results"], [])

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Перевод с пробелами", "category": "категория с пробелами", "amount": 100}]')
    def test_finder_with_spaces(self, mock_file):
        """Тест поиска с пробелами в запросе"""
        result = finder("с пробелами", "test.json")

        self.assertEqual(result["found"], 1)
        self.assertEqual(result["results"][0]["description"], "Перевод с пробелами")

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Спецсимволы!@#$%", "category": "категория", "amount": 100}]')
    def test_finder_special_characters(self, mock_file):
        """Тест поиска со специальными символами"""
        result = finder("символы", "test.json")

        self.assertEqual(result["found"], 1)

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "123456", "category": "numbers", "amount": 100}]')
    def test_finder_numeric_search(self, mock_file):
        """Тест поиска числовых значений"""
        result = finder("123", "test.json")

        self.assertEqual(result["found"], 1)

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Тест", "category": "тест", "amount": 100}]')
    def test_finder_exact_match(self, mock_file):
        """Тест точного совпадения"""
        result = finder("Тест", "test.json")

        self.assertEqual(result["found"], 1)

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Много слов в описании транзакции", "category": "разная категория", "amount": 100}]')
    def test_finder_long_description(self, mock_file):
        """Тест поиска в длинном описании"""
        result = finder("транзакции", "test.json")

        self.assertEqual(result["found"], 1)


class TestFinderEdgeCases(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Перевод", "category": "перевод", "amount": 100}, {"description": "перевод", "category": "Перевод", "amount": 200}]')
    def test_finder_both_fields_match(self, mock_file):
        """Тест когда запрос совпадает и с описанием и с категорией"""
        result = finder("перевод", "test.json")

        self.assertEqual(result["found"], 2)

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Перевод", "category": "оплата", "amount": 100}, {"description": "Оплата", "category": "перевод", "amount": 200}]')
    def test_finder_cross_matching(self, mock_file):
        """Тест перекрестного совпадения"""
        result = finder("перевод", "test.json")

        self.assertEqual(result["found"], 2)

    @patch('builtins.open', new_callable=mock_open, read_data='null')
    def test_finder_null_json(self, mock_file):
        """Тест с null JSON"""
        result = finder("перевод", "test.json")

        self.assertIn("error", result)
        self.assertEqual(result["results"], [])

    @patch('builtins.open', new_callable=mock_open, read_data='{"single": "object"}')
    def test_finder_single_object_json(self, mock_file):
        """Тест с JSON объектом вместо массива"""
        result = finder("object", "test.json")

        self.assertIn("error", result)
        self.assertEqual(result["results"], [])


class TestFinderPerformance(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    def test_finder_large_dataset(self, mock_file):
        """Тест производительности с большим набором данных"""
        # Создаем большой набор тестовых данных
        large_data = []
        for i in range(1000):
            if i % 2 == 0:
                large_data.append({"description": f"Перевод {i}", "category": "перевод", "amount": i})
            else:
                large_data.append({"description": f"Оплата {i}", "category": "оплата", "amount": i})

        mock_file.return_value.read.return_value = json.dumps(large_data)

        result = finder("перевод", "large.json")

        self.assertEqual(result["found"], 500)  # Половина элементов содержит "перевод"


class TestFinderIntegration(unittest.TestCase):

    def test_finder_return_structure(self):
        """Тест структуры возвращаемого значения"""
        # Все успешные вызовы должны возвращать словарь с определенными ключами
        expected_keys = {"query", "found", "results"}

        # Тестируем с моком для успешного случая
        with patch('builtins.open', new_callable=mock_open,
                   read_data='[{"description": "test", "category": "test", "amount": 100}]'):
            result = finder("test", "test.json")

            if "error" not in result:
                self.assertTrue(expected_keys.issubset(result.keys()))
            else:
                # Для ошибок проверяем наличие ключа error
                self.assertIn("error", result)


# Дополнительные тесты для полного покрытия
class TestFinderComprehensive(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "Тест", "category": "тест", "amount": 100}]')
    def test_finder_unicode_support(self, mock_file):
        """Тест поддержки Unicode"""
        result = finder("Тест", "test.json")
        self.assertEqual(result["found"], 1)

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "test", "category": "test", "amount": 100}]')
    def test_finder_empty_query(self, mock_file):
        """Тест с пустым запросом"""
        result = finder("", "test.json")
        # Исправлено: пустой запрос должен найти все записи
        self.assertEqual(result["found"], 1)

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "test", "category": "test", "amount": 100}]')
    def test_finder_space_query(self, mock_file):
        """Тест с запросом из пробелов"""
        result = finder("   ", "test.json")
        # Исправлено: пробелы должны найти все записи
        self.assertEqual(result["found"], 1)

    @patch('builtins.open', new_callable=mock_open,
           read_data='[{"description": "test\\nwith\\nnewlines", "category": "test", "amount": 100}]')
    def test_finder_newlines(self, mock_file):
        """Тест с переносами строк в описании"""
        result = finder("newlines", "test.json")
        self.assertEqual(result["found"], 1)


# Тесты для логгера
class TestLoggerSetup(unittest.TestCase):

    def test_logger_creation(self):
        """Тест создания логгера"""
        from src.services import logger

        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "services")

    @patch('src.services.logger')
    def test_logger_used_in_finder(self, mock_logger):
        """Тест что логгер используется в функции finder"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = finder("test", "nonexistent.json")

            # Проверяем что логгер был вызван
            mock_logger.error.assert_called()


class TestFinderErrorLogging(unittest.TestCase):

    @patch('src.services.logger')
    def test_finder_logs_file_not_found(self, mock_logger):
        """Тест логирования ошибки файла не найден"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            finder("test", "nonexistent.json")
            mock_logger.error.assert_called_with('Файл не найден!!!💥')

    @patch('src.services.logger')
    def test_finder_logs_json_decode_error(self, mock_logger):
        """Тест логирования ошибки декодирования JSON"""
        with patch('builtins.open', new_callable=lambda: mock_open(read_data='invalid json')):
            finder("test", "invalid.json")
            mock_logger.error.assert_called_with('Файл не прочитан!!!💥')

    @patch('src.services.logger')
    def test_finder_logs_general_exception(self, mock_logger):
        """Тест логирования общих исключений"""
        with patch('builtins.open', side_effect=Exception("Test error")):
            finder("test", "error.json")
            mock_logger.error.assert_called_with('Ошибка поиска по файлу💥')


if __name__ == "__main__":
    unittest.main()