from src.api_class import HeadHunterAPI
from src.file_manager import JSONSaver
from src.utils import filter_vacancies, get_top_vacancies, get_vacancies_by_salary, print_vacancies, sort_vacancies
from src.vacancy import Vacancy


def user_interaction():
    """Функция для взаимодействия с пользователем"""
    # Создание экземпляра класса для работы с API
    hh_api = HeadHunterAPI()

    # Ввод данных от пользователя
    search_query = input("Введите поисковый запрос: ").strip()
    top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
    salary_range = input("Введите диапазон зарплат (например: 100000-150000): ").strip()

    # Получение вакансий
    print("Получение вакансий с HeadHunter...")
    hh_vacancies = hh_api.get_vacancies(search_query)

    # Преобразование в объекты
    vacancies_list = Vacancy.cast_to_object_list(hh_vacancies)

    # Сохранение в файл
    json_saver = JSONSaver()
    for vacancy in vacancies_list:
        json_saver.add_vacancy(vacancy)

    # Фильтрация и сортировка
    filtered_vacancies = filter_vacancies(vacancies_list, filter_words)
    ranged_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)
    sorted_vacancies = sort_vacancies(ranged_vacancies)
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n)

    # Вывод результатов
    print(f"\nНайдено вакансий: {len(top_vacancies)}")
    print_vacancies(top_vacancies)


if __name__ == "__main__":
    user_interaction()
