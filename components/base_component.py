from typing import Pattern

import allure
from playwright.sync_api import Page, expect

from tools.logger import get_logger

logger = get_logger(__name__)


class BaseComponent:
    """
    Базовый компонент страницы.
    Содержит общие методы и интерфейс для всех дочерних компонентов.
    """
    def __init__(self, page: Page):
        """
        Конструктор базового компонента.

        :param page: Экземпляр страницы Playwright.
        """
        self.page = page

    def check_current_url(self, expected_url: Pattern[str]):
        """
        Проверяет, соответствует ли текущий URL страницы заданному шаблону.

        :param expected_url: Шаблон (регулярное выражение), которому должен соответствовать URL.
        """
        step = f'Checking that current url matches pattern "{expected_url.pattern}"'

        # Добавляем шаг в Allure отчёт
        with allure.step(step):
            logger.info(step)
            # Проверяем, что URL соответствует заданному шаблону
            expect(self.page).to_have_url(expected_url)

