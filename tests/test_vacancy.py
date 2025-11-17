import unittest

from src.vacancy import Vacancy


class TestVacancy(unittest.TestCase):
    """Тесты для класса Vacancy"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.vacancy_data = {
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/1",
            "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            "snippet": {"requirement": "Опыт работы с Python, Django", "responsibility": "Разработка веб-приложений"},
            "employer": {"name": "IT Company"},
            "experience": {"name": "от 1 года до 3 лет"},
        }

        self.vacancy_without_salary = {
            "name": "Python Developer",
            "alternate_url": "https://hh.ru/vacancy/2",
            "salary": None,
            "snippet": {"requirement": "Опыт работы с Python", "responsibility": "Разработка приложений"},
            "employer": {"name": "Startup"},
            "experience": {"name": "нет опыта"},
        }

    def test_vacancy_creation(self):
        """Тест создания вакансии"""
        vacancy = Vacancy(
            title="Python Developer",
            url="https://hh.ru/vacancy/1",
            salary_from=100000,
            salary_to=150000,
            description="Разработка приложений",
            requirements="Опыт работы с Python",
            company="IT Company",
            experience="от 1 года до 3 лет",
        )

        self.assertEqual(vacancy.title, "Python Developer")
        self.assertEqual(vacancy.url, "https://hh.ru/vacancy/1")
        self.assertEqual(vacancy.salary_from, 100000)
        self.assertEqual(vacancy.salary_to, 150000)
        self.assertEqual(vacancy.company, "IT Company")
        self.assertEqual(vacancy.experience, "от 1 года до 3 лет")

    def test_salary_validation(self):
        """Тест валидации зарплаты"""
        # Зарплата не указана
        vacancy = Vacancy(
            title="Developer",
            url="https://hh.ru/vacancy/1",
            salary_from=None,
            salary_to=None,
            description="Test",
            requirements="Test",
            company="Company",
            experience="нет опыта",
        )

        self.assertEqual(vacancy.salary_from, 0)
        self.assertEqual(vacancy.salary_to, 0)

    def test_str_representation(self):
        """Тест строкового представления"""
        vacancy = Vacancy(
            title="Python Developer",
            url="https://hh.ru/vacancy/1",
            salary_from=100000,
            salary_to=150000,
            description="Разработка",
            requirements="Python",
            company="IT Company",
            experience="1-3 года",
        )

        result = str(vacancy)
        self.assertIn("Python Developer", result)
        self.assertIn("IT Company", result)
        self.assertIn("100000-150000", result)

    def test_str_representation_no_salary(self):
        """Тест строкового представления без зарплаты"""
        vacancy = Vacancy(
            title="Developer",
            url="https://hh.ru/vacancy/1",
            salary_from=0,
            salary_to=0,
            description="Test",
            requirements="Test",
            company="Company",
            experience="нет опыта",
        )

        result = str(vacancy)
        self.assertIn("Зарплата не указана", result)

    def test_comparison_operators(self):
        """Тест операторов сравнения"""
        vacancy1 = Vacancy("Dev1", "url1", 100000, 150000, "desc1", "req1", "comp1", "exp1")
        vacancy2 = Vacancy("Dev2", "url2", 80000, 120000, "desc2", "req2", "comp2", "exp2")
        vacancy3 = Vacancy("Dev3", "url3", 100000, 150000, "desc3", "req3", "comp3", "exp3")

        # Больше
        self.assertTrue(vacancy1 > vacancy2)
        # Меньше
        self.assertTrue(vacancy2 < vacancy1)
        # Равны по зарплате
        self.assertFalse(vacancy1 > vacancy3)
        self.assertFalse(vacancy1 < vacancy3)

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        vacancy = Vacancy(
            title="Python Developer",
            url="https://hh.ru/vacancy/1",
            salary_from=100000,
            salary_to=150000,
            description="Разработка",
            requirements="Python",
            company="IT Company",
            experience="1-3 года",
        )

        result = vacancy.to_dict()

        self.assertEqual(result["title"], "Python Developer")
        self.assertEqual(result["url"], "https://hh.ru/vacancy/1")
        self.assertEqual(result["salary_from"], 100000)
        self.assertEqual(result["salary_to"], 150000)
        self.assertEqual(result["company"], "IT Company")
        self.assertEqual(result["experience"], "1-3 года")

    def test_cast_to_object_list(self):
        """Тест преобразования списка данных в объекты"""
        vacancies_data = [self.vacancy_data, self.vacancy_without_salary]

        vacancies = Vacancy.cast_to_object_list(vacancies_data)

        self.assertEqual(len(vacancies), 2)
        self.assertIsInstance(vacancies[0], Vacancy)
        self.assertIsInstance(vacancies[1], Vacancy)
        self.assertEqual(vacancies[0].title, "Python Developer")
        self.assertEqual(vacancies[1].title, "Python Developer")
        # Проверка валидации зарплаты
        self.assertEqual(vacancies[1].salary_from, 0)
        self.assertEqual(vacancies[1].salary_to, 0)

    def test_cast_to_object_list_empty_data(self):
        """Тест преобразования пустого списка"""
        vacancies = Vacancy.cast_to_object_list([])
        self.assertEqual(vacancies, [])

    def test_cast_to_object_list_missing_fields(self):
        """Тест преобразования с отсутствующими полями"""
        incomplete_data = [
            {
                "name": "Developer",
                "alternate_url": "https://hh.ru/vacancy/1",
                # Отсутствуют salary, snippet, employer, experience
            }
        ]

        vacancies = Vacancy.cast_to_object_list(incomplete_data)

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0].title, "Developer")
        self.assertEqual(vacancies[0].company, "Не указано")
        self.assertEqual(vacancies[0].salary_from, 0)

    def test_slots(self):
        """Тест использования __slots__"""
        vacancy = Vacancy("Title", "url", 100000, 150000, "desc", "req", "comp", "exp")

        with self.assertRaises(AttributeError):
            vacancy.non_existent_attr = "value"


if __name__ == "__main__":
    unittest.main()
