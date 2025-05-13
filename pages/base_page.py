from typing import Pattern
import re
import allure
from playwright.sync_api import Page, expect
from tools.routes import AppRoute
from tools.logger import get_logger
from config import Settings

logger = get_logger(__name__)


class BasePage:
    """
    Базовый класс для всех PageObject-страниц.

    Предоставляет общие методы для работы с веб-страницами:
    - Переход по URL с использованием маршрутов из AppRoute.
    - Перезагрузка текущей страницы.
    - Проверка текущего URL на соответствие маршруту или регулярному выражению.
    """

    def __init__(self, page: Page) -> None:
        """
        Инициализирует объект страницы.

        :param page: Экземпляр страницы Playwright для взаимодействия с браузером.
        """
        self.page = page

    def open(self, route: AppRoute) -> None:
        """
        Открывает страницу по указанному маршруту и ждёт полной загрузки.

        :param route: URN страницы
        """
        step = f'Opening the URN "{route.value}"'

        with allure.step(step):
            logger.info(step)
            try:
                self.page.goto(route, wait_until='domcontentloaded')
                logger.info(f"Opened URL: {self.page.url}")
            except Exception as e:
                logger.error(f"Failed to open {route}: {e}")
                raise

    def reload(self) -> None:
        """
        Перезагружает текущую страницу и ждёт полной загрузки.
        """
        step = f'Reloading page with url "{self.page.url}"'

        with allure.step(step):
            logger.info(step)
            self.page.reload(wait_until='domcontentloaded')

    def check_current_url(self, expected_url: Pattern[str]) -> None:
        """
        Проверяет, что текущий URL соответствует ожидаемому регулярному выражению.

        :param expected_url: Ожидаемый URL как регулярное выражение (Pattern)
        """
        step = f'Checking that current url matches pattern "{expected_url.pattern}"'

        with allure.step(step):
            logger.info(step)
            # Проверка соответствия текущего URL
            expect(self.page).to_have_url(expected_url)