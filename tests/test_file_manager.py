import json
import os
import unittest
from unittest.mock import mock_open, patch

from src.file_manager import FileManager, JSONSaver
from src.vacancy import Vacancy


class TestJSONSaver(unittest.TestCase):
    """Тесты для класса JSONSaver"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.saver = JSONSaver("test_vacancies.json")
        self.vacancy = Vacancy(
            title="Python Developer",
            url="https://hh.ru/vacancy/1",
            salary_from=100000,
            salary_to=150000,
            description="Разработка",
            requirements="Python",
            company="IT Company",
            experience="1-3 года",
        )

    def tearDown(self):
        """Очистка после каждого теста"""
        if os.path.exists("test_vacancies.json"):
            os.remove("test_vacancies.json")

    def test_inheritance(self):
        """Тест наследования от абстрактного класса"""
        self.assertIsInstance(self.saver, FileManager)

    def test_initialization(self):
        """Тест инициализации"""
        self.assertEqual(self.saver._filename, "test_vacancies.json")

        # Тест значения по умолчанию
        default_saver = JSONSaver()
        self.assertEqual(default_saver._filename, "vacancies.json")

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps([]))
    def test_add_vacancy_new(self, mock_file):
        """Тест добавления новой вакансии"""
        self.saver.add_vacancy(self.vacancy)

        # Проверяем, что файл был открыт для записи
        mock_file.assert_called_with("test_vacancies.json", "w", encoding="utf-8")

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps([{"url": "https://hh.ru/vacancy/1"}]))
    def test_add_vacancy_duplicate(self, mock_file):
        """Тест добавления дублирующей вакансии"""
        self.saver.add_vacancy(self.vacancy)

        # Файл не должен быть перезаписан (дубликат)
        write_calls = [call for call in mock_file.mock_calls if call[0] == "().write"]
        self.assertEqual(len(write_calls), 0)

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps([{"url": "https://hh.ru/vacancy/2"}]))
    def test_add_vacancy_unique(self, mock_file):
        """Тест добавления уникальной вакансии"""
        self.saver.add_vacancy(self.vacancy)

        # Файл должен быть открыт для записи
        mock_file.assert_called_with("test_vacancies.json", "w", encoding="utf-8")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            [{"title": "Python Developer", "url": "https://hh.ru/vacancy/1", "company": "IT Company"}]
        ),
    )
    def test_get_vacancies_with_criteria(self, mock_file):
        """Тест получения вакансий по критериям"""
        criteria = {"title": "Python"}
        vacancies = self.saver.get_vacancies(criteria)

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]["title"], "Python Developer")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            [{"title": "Python Developer", "url": "https://hh.ru/vacancy/1", "company": "IT Company"}]
        ),
    )
    def test_get_vacancies_exact_match(self, mock_file):
        """Тест получения вакансий по точному совпадению"""
        criteria = {"company": "IT Company"}
        vacancies = self.saver.get_vacancies(criteria)

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]["company"], "IT Company")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps([{"title": "Java Developer", "url": "https://hh.ru/vacancy/2", "company": "Tech Corp"}]),
    )
    def test_get_vacancies_no_match(self, mock_file):
        """Тест получения вакансий без совпадений"""
        criteria = {"title": "Python"}
        vacancies = self.saver.get_vacancies(criteria)

        self.assertEqual(len(vacancies), 0)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            [
                {
                    "title": "Java Developer",
                    "url": "https://hh.ru/vacancy/2",
                    "salary_from": 120000,
                    "salary_to": 180000,
                    "description": "Java разработка",
                    "requirements": "Java, Spring",
                    "company": "Tech Corp",
                    "experience": "3-5 лет",
                }
            ]
        ),
    )
    def test_delete_vacancy(self, mock_file):
        """Тест удаления вакансии"""
        vacancy_to_delete = Vacancy(
            title="Java Developer",
            url="https://hh.ru/vacancy/2",
            salary_from=120000,
            salary_to=180000,
            description="Java разработка",
            requirements="Java, Spring",
            company="Tech Corp",
            experience="3-5 лет",
        )

        self.saver.delete_vacancy(vacancy_to_delete)

        # Проверяем, что файл был открыт для записи
        mock_file.assert_called_with("test_vacancies.json", "w", encoding="utf-8")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_vacancies_file_not_found(self, mock_file):
        """Тест загрузки при отсутствии файла"""
        vacancies = self.saver._load_vacancies()
        self.assertEqual(vacancies, [])

    def test_save_and_load_integration(self):
        """Интеграционный тест сохранения и загрузки"""
        # Сохраняем вакансию
        self.saver.add_vacancy(self.vacancy)

        # Загружаем вакансии
        vacancies = self.saver._load_vacancies()

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]["title"], "Python Developer")
        self.assertEqual(vacancies[0]["url"], "https://hh.ru/vacancy/1")

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps([]))
    def test_get_vacancies_empty_file(self, mock_file):
        """Тест получения вакансий из пустого файла"""
        criteria = {"title": "Python"}
        vacancies = self.saver.get_vacancies(criteria)

        self.assertEqual(len(vacancies), 0)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            [{"title": "Senior Python Developer", "url": "https://hh.ru/vacancy/3", "company": "Big Tech"}]
        ),
    )
    def test_get_vacancies_partial_match(self, mock_file):
        """Тест получения вакансий по частичному совпадению"""
        criteria = {"title": "Python"}
        vacancies = self.saver.get_vacancies(criteria)

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]["title"], "Senior Python Developer")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            [
                {
                    "title": "Python Developer",
                    "url": "https://hh.ru/vacancy/1",
                    "salary_from": 100000,
                    "salary_to": 150000,
                }
            ]
        ),
    )
    def test_get_vacancies_numeric_criteria(self, mock_file):
        """Тест получения вакансий по числовым критериям"""
        criteria = {"salary_from": 100000}
        vacancies = self.saver.get_vacancies(criteria)

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]["salary_from"], 100000)


if __name__ == "__main__":
    unittest.main()
