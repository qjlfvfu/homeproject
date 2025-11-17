import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .vacancy import Vacancy


class FileManager(ABC):
    """Абстрактный класс для работы с файлами"""

    @abstractmethod
    def add_vacancy(self, vacancy: Vacancy) -> None:
        pass

    @abstractmethod
    def get_vacancies(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy: Vacancy) -> None:
        pass


class JSONSaver(FileManager):
    """Класс для сохранения информации о вакансиях в JSON-файл"""

    def __init__(self, filename: str = "vacancies.json"):
        self._filename = filename

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавление вакансии в файл"""
        vacancies = self._load_vacancies()

        # Проверка на дубликаты
        if not any(v["url"] == vacancy.url for v in vacancies):
            vacancies.append(vacancy.to_dict())
            self._save_vacancies(vacancies)

    def get_vacancies(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получение вакансий по критериям"""
        vacancies = self._load_vacancies()
        filtered_vacancies = []

        for vacancy in vacancies:
            matches = True
            for key, value in criteria.items():
                if key in vacancy:
                    vacancy_value = str(vacancy[key]).lower()
                    search_value = str(value).lower()

                    # Поиск частичного совпадения для строк
                    if isinstance(value, str) and search_value not in vacancy_value:
                        matches = False
                        break
                    # Точное совпадение для чисел и других типов
                    elif not isinstance(value, str) and vacancy[key] != value:
                        matches = False
                        break
                else:
                    # Ключ отсутствует в вакансии
                    matches = False
                    break

            if matches:
                filtered_vacancies.append(vacancy)

        return filtered_vacancies

    def delete_vacancy(self, vacancy: Vacancy) -> None:
        """Удаление вакансии из файла"""
        vacancies = self._load_vacancies()
        vacancies = [v for v in vacancies if v["url"] != vacancy.url]
        self._save_vacancies(vacancies)

    def _load_vacancies(self) -> List[Dict[str, Any]]:
        """Загрузка вакансий из файла"""
        try:
            with open(self._filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def _save_vacancies(self, vacancies: List[Dict[str, Any]]) -> None:
        """Сохранение вакансий в файл"""
        with open(self._filename, "w", encoding="utf-8") as f:
            json.dump(vacancies, f, ensure_ascii=False, indent=2)
