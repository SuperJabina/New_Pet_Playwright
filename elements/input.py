import allure
from playwright.sync_api import expect, Locator

from elements.base_element import BaseElement
from tools.logger import get_logger

logger = get_logger(__name__)


class Input(BaseElement):
    """
    Класс для работы с полями ввода на странице. Наследует базовые методы от BaseElement
    и добавляет специфичные методы для работы с полями ввода, такие как заполнение значений
    и проверка значений в поле.
    """

    @property
    def type_of(self) -> str:
        """
        Возвращает тип элемента, в данном случае "input".
        Это полезно для унификации работы с различными типами элементов.
        """
        return "input"

    def fill(self, value: str, nth: int = 0):
        """
        Заполняет поле ввода заданным значением.

        :param value: Значение, которое нужно ввести в поле.
        :param nth: Индекс, если на странице несколько одинаковых элементов.
        :raises AssertionError: Если поле не найдено или не доступно для ввода.
        """
        step = f'Filling {self.type_of} "{self.name}" to value "{value}"'

        with allure.step(step):
            locator = self.get_locator(nth)
            logger.info(step)
            locator.fill(value)

    def check_have_value(self, value: str, nth: int = 0) -> bool:
        """
        Проверяет, что поле ввода содержит заданное значение.

        Args:
            value: Ожидаемое значение в поле ввода.
            nth: Индекс, если на странице несколько одинаковых элементов.

        Returns:
            bool: True, если значение совпадает.

        Raises:
            ValueError: Если элемент не видим или не удалось проверить значение.
            AssertionError: Если значение не соответствует ожидаемому.
        """
        step = f'Checking that {self.type_of} "{self.name}" has a value "{value}"'

        with allure.step(step):
            locator = self.get_locator(nth)
            logger.info(step)
            try:
                expect(locator).to_have_value(value)
                allure.attach(
                    f"Value for {self.name} matches: {value}",
                    name=f"Value Check ({self.name})",
                    attachment_type=allure.attachment_type.TEXT
                )
                return True
            except Exception as e:
                err = f"Value check failed for {self.name}: expected '{value}', got error: {str(e)}"
                logger.error(err)
                allure.attach(err, name=f"Value Check Error ({self.name})", attachment_type=allure.attachment_type.TEXT)
                raise