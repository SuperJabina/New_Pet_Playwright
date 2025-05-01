import allure
from playwright.sync_api import expect, Locator

from elements.base_element import BaseElement
from tools.logger import get_logger

logger = get_logger(__name__)


class Button(BaseElement):
    """
    Класс для работы с кнопками на странице. Наследует базовые методы от BaseElement и добавляет
    специфичные методы для работы с кнопками, такие как проверка состояния (включена/выключена).
    """

    @property
    def type_of(self) -> str:
        """
        Возвращает тип элемента, в данном случае "button".
        Используется для унификации логирования и обработки элементов.
        """
        return "button"

    def check_enabled(self, locator: Locator) -> bool:
        """
        Проверяет, что кнопка активна (включена). Используется для тестирования сценариев,
        когда кнопка должна быть доступна для клика.

        :param locator: Объект типа Locator
        :return: True, если элемент активен, False, если неактивен
        """
        step = f'Checking that {self.type_of} "{self.name}" is enabled'

        with allure.step(step):
            try:
                expect(locator).to_be_enabled()
                result = f"Element {self.type_of} '{self.name}' is enabled"
                logger.info(result)
                allure.attach(
                    result,
                    name="Is enabled",
                    attachment_type=allure.attachment_type.TEXT
                )
                return True
            except Exception as e:
                err = f"Element {self.type_of} '{self.name}' is disabled: {e}"
                logger.error(err)
                allure.attach(
                    err,
                    name="Is disabled",
                    attachment_type=allure.attachment_type.TEXT
                )
                return False
