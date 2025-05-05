from enum import Enum


class AppRoute(str, Enum):
    """
    Enum со всеми основными маршрутами приложения.
    Наследуется от str, чтобы значения можно было использовать как обычные строки.

    Примеры:
    - переходы в тестах;
    - проверка текущего URL;
    - редиректы.
    """
    LOGIN = "./#/auth/login"  # Страница входа
    REGISTRATION = "./#/auth/registration"  # Страница регистрации

    DASHBOARD = "./#/dashboard"  # Главная страница (дашборд)

    COURSES = "./#/courses"  # Список курсов
    COURSES_CREATE = "./#/courses/create"  # Создание нового курса
    WEB_TABLES = "./webtables" # Страница для тестирования таблицы