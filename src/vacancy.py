from typing import Any, Dict, List


class Vacancy:
    """Класс для работы с вакансиями"""

    __slots__ = [
        "_title",
        "_url",
        "_salary_from",
        "_salary_to",
        "_description",
        "_requirements",
        "_company",
        "_experience",
    ]

    def __init__(
        self,
        title: str,
        url: str,
        salary_from: int,
        salary_to: int,
        description: str,
        requirements: str,
        company: str,
        experience: str,
    ):
        self._title = title
        self._url = url
        self._salary_from = self._validate_salary(salary_from)
        self._salary_to = self._validate_salary(salary_to)
        self._description = description
        self._requirements = requirements
        self._company = company
        self._experience = experience

    def _validate_salary(self, salary: int) -> int:
        """Приватный метод валидации зарплаты"""
        return salary if salary is not None else 0

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url

    @property
    def salary_from(self) -> int:
        return self._salary_from

    @property
    def salary_to(self) -> int:
        return self._salary_to

    @property
    def description(self) -> str:
        return self._description

    @property
    def requirements(self) -> str:
        return self._requirements

    @property
    def company(self) -> str:
        return self._company

    @property
    def experience(self) -> str:
        return self._experience

    def __str__(self) -> str:
        salary_info = f"{self._salary_from}-{self._salary_to}" if self._salary_from > 0 else "Зарплата не указана"
        return (
            f"Вакансия: {self._title}\n"
            f"Компания: {self._company}\n"
            f"Зарплата: {salary_info}\n"
            f"Опыт: {self._experience}\n"
            f"Ссылка: {self._url}\n"
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return (self._salary_from + self._salary_to) < (other._salary_from + other._salary_to)

    def __gt__(self, other) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return (self._salary_from + self._salary_to) > (other._salary_from + other._salary_to)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self._title,
            "url": self._url,
            "salary_from": self._salary_from,
            "salary_to": self._salary_to,
            "description": self._description,
            "requirements": self._requirements,
            "company": self._company,
            "experience": self._experience,
        }

    @classmethod
    def cast_to_object_list(cls, vacancies_data: List[Dict[str, Any]]) -> List["Vacancy"]:
        vacancies = []
        for vacancy_data in vacancies_data:
            salary = vacancy_data.get("salary", {}) or {}
            snippet = vacancy_data.get("snippet", {}) or {}
            employer = vacancy_data.get("employer", {}) or {}
            experience = vacancy_data.get("experience", {}) or {}

            vacancy = cls(
                title=vacancy_data.get("name", "Не указано"),
                url=vacancy_data.get("alternate_url", ""),
                salary_from=salary.get("from") if salary else 0,
                salary_to=salary.get("to") if salary else 0,
                description=snippet.get("responsibility", "Описание отсутствует"),
                requirements=snippet.get("requirement", "Требования не указаны"),
                company=employer.get("name", "Не указано"),
                experience=experience.get("name", "Не указано"),
            )
            vacancies.append(vacancy)

        return vacancies
