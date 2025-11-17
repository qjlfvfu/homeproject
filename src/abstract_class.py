from abc import ABC, abstractmethod
from typing import Dict, List


class VacancyAPI(ABC):
    """Абстрактный класс только для работы с API"""

    @abstractmethod
    def get_vacancies(self, keyword: str, **kwargs) -> List[Dict]:
        pass


class DataFormatter(ABC):
    """Абстрактный класс для форматирования данных"""

    @abstractmethod
    def format_vacancy(self, raw_data: Dict) -> Dict:
        pass


class DataSaver(ABC):
    """Абстрактный класс для сохранения данных"""

    @abstractmethod
    def save_vacancies(self, vacancies: List[Dict]) -> None:
        pass
