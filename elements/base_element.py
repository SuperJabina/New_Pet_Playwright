from typing import Union, List

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
                # Ожидаем появления элемента в DOM в течение 5 секунд
                self.locator.nth(nth).wait_for(state="attached", timeout=7000)
                locator = self.locator.nth(nth)
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
            try:
                logger.info(step)
                locator = self.get_locator(nth)
                assert locator.is_enabled(), f"Element {self.name} is not enabled"
                self.locator.click()
            except Exception as e:
                logger.error(f"Error clicking submit button: {e}")
                raise

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
                    name=f"Visibility Check({self.name})",
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

    def check_have_text(self, text: str, nth: int = 0):
        """
        Проверяет, что у элемента присутствует заданный текст.

        :param text: Ожидаемый текст
        :param nth: Индекс элемента
        """
        step = f'Checking that {self.type_of} "{self.name}" has text "{text}"'

        with allure.step(step):
            locator = self.get_locator(nth)
            logger.info(step)
            expect(locator).to_have_text(text)

    def get_css_property(self, css_property, nth: int = 0):

        locator = self.get_locator(nth)

        # Получаем значение CSS-свойства
        step = f'Getting CSS property {self.type_of} "{self.name}"'
        logger.info(step)
        try:
            property_value = locator.evaluate(
                """(element, cssProperty) => {
                    return window.getComputedStyle(element).getPropertyValue(cssProperty);
                }""",
                css_property
            )
            allure.attach(
                f'CSS property {css_property} is: {property_value}',
                name=f"CSS Property ({self.name}, {css_property})",
                attachment_type=allure.attachment_type.TEXT
            )
            return property_value
        except Exception as e:
            err = f'error getting CSS property {self.type_of} "{self.name}": {str(e)}'
            logger.error(err)
            raise Exception(err)

    def get_text_from_element(self, nth: int = 0, all_elements: bool = False) -> Union[str, List[str]]:
        """
            Получает текст одного элемента или группы элементов.

            Args:
                nth: Индекс элемента (для одного элемента).
                all_elements: Если True, возвращает текст всех элементов, иначе — одного.

            Returns:
                str: Текст одного элемента (если all_elements=False).
                List[str]: Список текстов всех элементов (если all_elements=True).

            Raises:
                ValueError: Если элемент не найден или не удалось получить текст.
            """
        locator = self.get_locator(nth)
        step = f'Getting text from {self.type_of} "{self.name}"'
        logger.info(step)
        try:
            if all_elements:
                texts = locator.all_inner_texts()
            else:
                texts = locator.inner_text()

            allure.attach(
                f'Received text from {self.name}: {texts}',
                name=f"Text from {self.name}",
                attachment_type=allure.attachment_type.TEXT
            )
            return texts
        except Exception as e:
            err = f'error getting text from {self.type_of} "{self.name}": {str(e)}'
            logger.error(err)
            raise Exception(err)