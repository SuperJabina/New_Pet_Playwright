import allure
from playwright.sync_api import Page, Locator, expect

from tools.logger import get_logger

logger = get_logger(__name__)

class BaseElement:
    """
    Базовый элемент страницы.

    Предоставляет общие методы взаимодействия с любым UI-элементом,
    включая клик, проверку видимости, проверку текста и получение локатора.
    """
    def __init__(self, page: Page, locator: Locator, name: str) -> None:
        """
        :param page: Экземпляр страницы Playwright
        :param locator: Объект типа Locator
        :param name: Название элемента (для логирования и аллюра)
        """
        self.page = page
        self.name = name
        self.locator = locator

    @property
    def type_of(self) -> str:
        """
        Возвращает тип элемента. Переопределяется в потомках.
        """
        return "base element"

    def click(self, locator: Locator) -> None:
        """
        Выполняет клик по элементу.

        :param locator: Объект типа Locator
        """
        step = f'Clicking {self.type_of} "{self.name}"'
        logger.debug(step)

        with allure.step(step):
            count = locator.count()
            if count == 1:
                try:
                    locator.click()
                    logger.info(f"Successfully clicked {self.type_of} '{self.name}'")
                except Exception as e:
                    err = f"Failed to click {self.type_of} '{self.name}' : {e}"
                    logger.error(err)
                    raise TimeoutError(err)
            else:
                err = f"Найдено {count} элементов {self.type_of} '{self.name}'. Ожидался ровно один."
                logger.error(err)
                raise ValueError(err)

    def check_visible(self, locator: Locator) -> bool:
        """
        Проверяет, что элемент видим на странице.

        :param locator: Объект типа Locator
        :return: True, если элемент видим, False, если невидим
        """
        step = f'Checking that {self.type_of} "{self.name}" is visible'

        with allure.step(step):
            try:
                expect(locator).to_be_visible()
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

    def check_have_text(self, text: str, nth: int = 0, **kwargs):
        """
        Проверяет, что у элемента присутствует заданный текст.

        :param text: Ожидаемый текст
        :param nth: Индекс элемента
        :param kwargs: Аргументы для форматирования локатора
        """
        step = f'Checking that {self.type_of} "{self.name}" has text "{text}"'

        with allure.step(step):
            locator = self.get_locator(nth, **kwargs)
            logger.info(step)
            expect(locator).to_have_text(text)