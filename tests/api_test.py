import unittest
from unittest.mock import Mock, patch

import requests

from src.api_class import HeadHunterAPI, VacancyAPI


class TestHeadHunterAPI(unittest.TestCase):
    """Тесты для класса HeadHunterAPI"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.api = HeadHunterAPI()
        self.mock_response = {
            "items": [
                {
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/1",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "snippet": {"requirement": "Опыт работы с Python", "responsibility": "Разработка приложений"},
                    "employer": {"name": "IT Company"},
                    "experience": {"name": "от 1 года до 3 лет"},
                }
            ]
        }

    def test_inheritance(self):
        """Тест наследования от абстрактного класса"""
        self.assertIsInstance(self.api, VacancyAPI)

    def test_initialization(self):
        """Тест инициализации класса"""
        self.assertEqual(self.api._base_url, "https://api.hh.ru/vacancies")
        self.assertIn("User-Agent", self.api._headers)

    @patch("src.api.requests.get")
    def test_connect_to_api_success(self, mock_get):
        """Тест успешного подключения к API"""
        # Мокаем ответ
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.api._connect_to_api({"text": "python"})

        self.assertEqual(result, self.mock_response)
        mock_get.assert_called_once()

    @patch("src.api.requests.get")
    def test_connect_to_api_failure(self, mock_get):
        """Тест ошибки при подключении к API"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        with self.assertRaises(requests.exceptions.RequestException):
            self.api._connect_to_api({"text": "python"})

    @patch("src.api.HeadHunterAPI._connect_to_api")
    def test_get_vacancies_success(self, mock_connect):
        """Тест успешного получения вакансий"""
        mock_connect.return_value = self.mock_response

        vacancies = self.api.get_vacancies("python")

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]["name"], "Python Developer")
        mock_connect.assert_called_once_with(
            {"text": "python", "per_page": 100, "area": 113, "only_with_salary": True}
        )

    @patch("src.api.HeadHunterAPI._connect_to_api")
    def test_get_vacancies_empty_response(self, mock_connect):
        """Тест получения пустого ответа"""
        mock_connect.return_value = {}

        vacancies = self.api.get_vacancies("python")

        self.assertEqual(vacancies, [])

    @patch("src.api.HeadHunterAPI._connect_to_api")
    def test_get_vacancies_api_error(self, mock_connect):
        """Тест ошибки API"""
        mock_connect.side_effect = requests.exceptions.RequestException("API Error")

        vacancies = self.api.get_vacancies("python")

        self.assertEqual(vacancies, [])


if __name__ == "__main__":
    unittest.main()
