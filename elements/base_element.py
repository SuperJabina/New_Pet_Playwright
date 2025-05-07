import allure
from playwright.sync_api import Page, Locator, expect
from tools.logger import get_logger

# Инициализация логгера
logger = get_logger(__name__)

class BaseElement:
    """Универсальный класс для работы с элементами страницы через Playwright.

    Позволяет:
    - Работать с переданным локатором Playwright
    - Поддерживает одиночные элементы и группы
    - Поддерживает основные методы взаимодействия
    """
    def __init__(
            self,
            page: Page,
            locator: Locator,
            name: str,
    ) -> None:
        """Инициализация элемента.

        Args:
            page: Экземпляр страницы Playwright
            locator: Готовый локатор Playwright
            name: Имя элемента (для логов и отчетов)
        """
        self.page: Page = page
        self.locator: Locator = locator
        self.name: str = name

    @property
    def type_of(self) -> str:
        """Возвращает тип элемента (может переопределяться в наследниках).

        Returns:
            Строку с описанием типа элемента
        """
        return "base element"

    def get_locator(self, nth: int = 0) -> Locator:
        """Возвращает локатор с учетом позиции элемента в группе.

        Args:
            nth: Индекс элемента в группе (0 - первый элемент)

        Returns:
            Locator: Готовый локатор Playwright

        Raises:
            ValueError: Если элемент не найден
        """
        step = f'Получение локатора для "{self.name}" (индекс: {nth})'
        with allure.step(step):
            try:
                locator = self.locator.nth(nth)
                if locator.count() == 0:
                    err = f"Элемент '{self.name}' не найден"
                    logger.warning(f"{step}, {err}")
                    raise ValueError(err)
                logger.info(f"{step}, найдено {locator.count()} элементов")
                return locator
            except Exception as e:
                err = f"Ошибка получения локатора для '{self.name}': {str(e)}"
                logger.error(f"{step}, {err}")
                raise ValueError(err) from e

    # --- Основные методы взаимодействия с элементами ---

    def click(self, nth: int = 0) -> None:
        """Выполняет клик по элементу.

        Args:
            nth: Индекс элемента в группе
        """
        step = f'Clicking {self.type_of} "{self.name}" (индекс: {nth})'
        with allure.step(step):
            logger.info(step)
            self.get_locator(nth).click()

    def check_visible(self, nth: int = 0) -> bool:
        """
        Проверяет, что элемент видим на странице.

        :param nth: Индекс элемента
        :return: True, если элемент видим, False, если невидим
        """
        step = f'Checking that {self.type_of} "{self.name}" is visible'

        with allure.step(step):
            try:
                expect(self.get_locator(nth)).to_be_visible()
                result = f"Element {self.type_of} '{self.name}' is visible"
                logger.info(result)
                allure.attach(
                    result,
                    name="Visibility Check",
                    attachment_type=allure.attachment_type.TEXT
                )
                return True
            except Exception as e:
                err = f"Element {self.type_of} '{self.name}' is not visible: {e}"
                logger.error(err)
                allure.attach(
                    err,
                    name="Visibility Check Error",
                    attachment_type=allure.attachment_type.TEXT
                )
                return False
