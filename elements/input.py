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

    def get_locator(self, nth: int = 0, **kwargs) -> Locator:
        """
        Получает локатор для поля ввода с возможностью параметризации и выбором индекса.
        """
        # Вызываем родительский метод для получения базового локатора и добавляем локатор для input
        # Может быть необходимо если на странице нужно как-то хитро получать поле ввода
        return super().get_locator(nth, **kwargs).locator('input')

    def fill(self, value: str, nth: int = 0, **kwargs):
        """
        Заполняет поле ввода заданным значением.

        :param value: Значение, которое нужно ввести в поле.
        :param nth: Индекс, если на странице несколько одинаковых элементов.
        :param kwargs: Дополнительные аргументы для параметризации локатора.
        :raises AssertionError: Если поле не найдено или не доступно для ввода.
        """
        step = f'Fill {self.type_of} "{self.name}" to value "{value}"'

        with allure.step(step):
            locator = self.get_locator(nth, **kwargs)
            logger.info(step)
            locator.fill(value)

    def check_have_value(self, value: str, nth: int = 0, **kwargs):
        """
        Проверяет, что поле ввода содержит заданное значение.

        :param value: Ожидаемое значение в поле ввода.
        :param nth: Индекс, если на странице несколько одинаковых элементов.
        :param kwargs: Дополнительные аргументы для параметризации локатора.
        :raises AssertionError: Если значение в поле не соответствует ожидаемому.
        """
        step = f'Checking that {self.type_of} "{self.name}" has a value "{value}"'

        with allure.step(step):
            locator = self.get_locator(nth, **kwargs)
            logger.info(step)
            expect(locator).to_have_value(value)