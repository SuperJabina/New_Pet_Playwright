from pathlib import Path

import pytest
import allure
from config import Settings

def pytest_addoption(parser):
    """Пользовательские опции командной строки"""
    parser.addoption('--browser-name', action='store', default=None, help="Browser to use for tests: chromium, firefox, webkit, remote_browser")

@pytest.fixture()
def settings(request) -> Settings:
    """
    Фикстура создаёт объект с настройками один раз на всю тестовую сессию.

    :param request: Объект pytest для доступа к аргументам командной строки.
    :return: Экземпляр класса Settings с загруженными конфигурациями.
    """
    browser_name = request.config.getoption("--browser-name")
    valid_browsers = ["chromium", "webkit", "firefox", "remote_browser"]
    if browser_name and browser_name not in valid_browsers:
        raise ValueError(f"Invalid browser: {browser_name}. Choose from {valid_browsers}")
    return Settings.initialize(browser_name=browser_name)

# Фикстура для добавления параметров в Allure
@pytest.fixture(autouse=True)
def add_browser_label(settings):
    """
    Автоматически добавляет параметры browser и locale в Allure-отчёт для каждого теста.
    """
    allure.dynamic.tag(settings.browser_name)