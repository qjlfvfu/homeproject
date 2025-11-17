from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests


class VacancyAPI(ABC):
    """Абстрактный класс для работы с API сервиса с вакансиями"""

    @abstractmethod
    def get_vacancies(self, search_query: str) -> List[Dict[str, Any]]:
        pass


class HeadHunterAPI(VacancyAPI):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self._base_url = "https://api.hh.ru/vacancies"
        self._headers = {"User-Agent": "HH-User-Agent"}

    def _connect_to_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Приватный метод подключения к API"""
        response = requests.get(self._base_url, headers=self._headers, params=params)
        response.raise_for_status()  # Проверка статус-кода
        return response.json()

    def get_vacancies(self, search_query: str) -> List[Dict[str, Any]]:
        """Получение вакансий по поисковому запросу"""
        params = {
            "text": search_query,
            "per_page": 10,
            "area": 113,  # Россия
            "only_with_salary": True,
        }

        try:
            data = self._connect_to_api(params)
            return data.get("items", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return []
