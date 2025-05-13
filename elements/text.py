import allure
from playwright.sync_api import expect

from elements.base_element import BaseElement
from tools.logger import get_logger

logger = get_logger(__name__)


class Text(BaseElement):
    """
    Класс для работы с текстом на странице. Наследует базовые методы от BaseElement и добавляет
    специфичные методы для работы с текстом, такие как .
    """

    @property
    def type_of(self) -> str:
        """
        Возвращает тип элемента, в данном случае "text".
        Используется для унификации логирования и обработки элементов.
        """
        return "text"

