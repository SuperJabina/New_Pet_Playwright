import allure
from playwright.sync_api import Page, Locator, expect
from typing import Optional, Dict, Any, Literal, Union, get_args, cast
from tools.logger import get_logger

# Инициализация логгера
logger = get_logger(__name__)

# Тип для стратегий локации
LocatorStrategy = Literal[
    "test_id",  # По data-testid атрибуту
    "css",  # CSS селектор
    "xpath",  # XPath выражение
    "text",  # Видимый текст
    "placeholder",  # Плейсхолдер поля
    "role"  # ARIA-роль
]

# Определяем допустимые ARIA-роли для стратегии by_role как Literal
# Полный список ARIA-ролей, поддерживаемых Playwright
AriaRoleLiteral = Literal[
    "alert", "alertdialog", "application", "article", "banner", "blockquote", "button",
    "caption", "cell", "checkbox", "code", "columnheader", "combobox", "complementary",
    "contentinfo", "definition", "deletion", "dialog", "directory", "document", "emphasis",
    "feed", "figure", "form", "generic", "grid",
    "gridcell", "group", "heading", "img", "insertion", "link", "list", "listbox",
    "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem",
    "menuitemcheckbox", "menuitemradio", "meter", "navigation", "none", "note", "option",
    "paragraph", "presentation", "progressbar", "radio", "radiogroup", "region", "row",
    "rowgroup", "rowheader", "scrollbar", "search", "searchbox", "separator", "slider",
    "spinbutton", "status", "strong", "subscript", "superscript", "switch", "tab",
    "table", "tablist", "tabpanel", "term", "textbox", "time", "timer", "toolbar",
    "tooltip", "tree", "treegrid", "treeitem"
]

class BaseElement:
    """Универсальный класс для работы с элементами страницы через Playwright.

    Позволяет:
    - Искать элементы разными стратегиями
    - Работать как с одиночными элементами, так и с группами
    - Поддерживает все основные методы взаимодействия
    """
    def __init__(
            self,
            page: Page,
            locator_value: Union[str, AriaRoleLiteral], # объединение (Union) строки (str) для других стратегий и Literal для ARIA-ролей
            name: str,
            strategy: LocatorStrategy = "text",
            locator_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Инициализация элемента.

        Args:
            page: Экземпляр страницы Playwright
            locator_value: Значение для поиска (селектор, текст и т.д.)
            name: Имя элемента (для логов и отчетов)
            strategy: Стратегия поиска элемента. По умолчанию 'text'
            locator_params: Дополнительные параметры для методов поиска Playwright
        """
        if strategy == "role" and locator_value not in get_args(AriaRoleLiteral):
            err = f"Недопустимая ARIA-роль: {locator_value}"
            logger.error(err)
            raise ValueError(err)
        self.page: Page = page
        self.name: str = name
        self.strategy: LocatorStrategy = strategy
        self.locator_value: Union[str, AriaRoleLiteral] = locator_value
        self.locator_params: Dict[str, Any] = locator_params or {}

    @property
    def type_of(self) -> str:
        """Возвращает тип элемента (может переопределяться в наследниках).

        Returns:
            Строку с описанием типа элемента
        """
        return "base element"

    def _get_base_locator(self) -> Locator:
        """Создает базовый локатор в зависимости от стратегии.

        Returns:
            Locator: Базовый локатор Playwright

        Raises:
            ValueError: Если передана неизвестная стратегия
        """
        if self.strategy == "test_id":
            # Поиск по data-testid атрибуту (без доп. параметров)
            return self.page.get_by_test_id(self.locator_value)

        elif self.strategy == "css":
            # CSS селектор
            return self.page.locator(self.locator_value)

        elif self.strategy == "xpath":
            # XPath выражение
            return self.page.locator(f"xpath={self.locator_value}")

        elif self.strategy == "text":
            # Поиск по тексту (поддерживает exact)
            return self.page.get_by_text(
                self.locator_value,
                exact=self.locator_params.get("exact", False),
                            )

        elif self.strategy == "placeholder":
            # Поиск по плейсхолдеру (поддерживает exact)
            return self.page.get_by_placeholder(
                self.locator_value,
                exact=self.locator_params.get("exact", False),
            )

        elif self.strategy == "role":
            role = cast(AriaRoleLiteral, self.locator_value) # Приведение типа для locator_value
            return self.page.get_by_role(
                role,  # Теперь тип соответствует Literal
                **{
                    k: v for k, v in self.locator_params.items()
                    if k in [
                        "checked", "disabled", "exact", "expanded",
                        "include_hidden", "level", "name", "pressed", "selected"
                    ]
                }
            )
        else:
            err = f"Неизвестная стратегия поиска элемента: {self.strategy}"
            logger.error(err)
            raise ValueError(err)

    def get_locator(self, nth: int = 0) -> Locator:
        """Возвращает локатор с учетом позиции элемента в группе.

        Args:
            nth: Индекс элемента в группе (0 - первый элемент)

        Returns:
            Locator: Готовый локатор Playwright
        """
        step = f'Получение локатора для "{self.name}" (индекс: {nth})'
        with allure.step(step):
            try:
                locator = self._get_base_locator().nth(nth)
                if locator.count() == 0:
                    err = f"Элемент '{self.name}' не найден (стратегия: {self.strategy}, значение: {self.locator_value})"
                    logger.warning(f"{step}, {err}")
                    raise ValueError(err)
                logger.info(
                    f"{step}, стратегия: {self.strategy}={self.locator_value}, найдено {locator.count()} элементов")
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
