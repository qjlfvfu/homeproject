import pytest
import pandas as pd
import os
import json
import tempfile
from datetime import datetime


class TestReportWriter:

    def test_decorator_without_filename(self):
        """Тест декоратора без указания имени файла."""
        from src.reports import report_writer  # замените на ваш модуль

        @report_writer()
        def test_function():
            return {"data": "test", "value": 123}

        # Создаем временную директорию для тестов
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                result = test_function()

                # Проверяем что файл создался
                files = os.listdir(temp_dir)
                report_files = [f for f in files if f.startswith('report_test_function_')]
                assert len(report_files) == 1

                # Проверяем содержимое файла
                with open(report_files[0], 'r', encoding='utf-8') as f:
                    file_content = json.load(f)

                assert file_content == result

            finally:
                os.chdir(original_dir)

    def test_decorator_with_filename(self):
        """Тест декоратора с указанием имени файла."""
        from src.reports import report_writer

        @report_writer("custom_report.json")
        def test_function():
            return {"test": "data"}

        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                result = test_function()

                assert os.path.exists("custom_report.json")

                with open("custom_report.json", 'r', encoding='utf-8') as f:
                    file_content = json.load(f)

                assert file_content == result

            finally:
                os.chdir(original_dir)

    def test_decorator_with_dataframe(self):
        """Тест декоратора с DataFrame."""
        from src.reports import report_writer

        @report_writer("dataframe_report.csv")
        def test_function():
            return pd.DataFrame({
                'col1': [1, 2, 3],
                'col2': ['a', 'b', 'c']
            })

        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                result = test_function()

                assert os.path.exists("dataframe_report.csv")

                # Проверяем что CSV файл можно прочитать
                df_from_file = pd.read_csv("dataframe_report.csv")
                pd.testing.assert_frame_equal(result, df_from_file)

            finally:
                os.chdir(original_dir)

    def test_different_file_extensions(self):
        """Тест разных расширений файлов."""
        from src.reports import report_writer

        test_cases = [
            ('report.json', 'json'),
            ('data.csv', 'csv'),
            ('analysis.xlsx', 'xlsx'),
            ('summary.txt', 'txt'),
            ('data', 'json')  # расширение по умолчанию
        ]

        for filename, expected_extension in test_cases:
            @report_writer(filename)
            def test_func():
                return {"test": "data"}

            with tempfile.TemporaryDirectory() as temp_dir:
                original_dir = os.getcwd()
                os.chdir(temp_dir)

                try:
                    test_func()

                    # Проверяем что файл создался с правильным расширением
                    final_filename = filename if '.' in filename else f"{filename}.{expected_extension}"
                    assert os.path.exists(final_filename)

                finally:
                    os.chdir(original_dir)

    def test_function_arguments_preserved(self):
        """Тест что аргументы функции сохраняются."""
        from src.reports import report_writer

        @report_writer()
        def func_with_args(a, b, c=10):
            return {"sum": a + b + c, "args": (a, b, c)}

        result = func_with_args(5, 3, c=2)
        assert result["sum"] == 10
        assert result["args"] == (5, 3, 2)