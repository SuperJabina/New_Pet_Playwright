import re

from playwright.sync_api import Page
from config import Settings
# from components.registration_form_component import RegistrationFormComponent
from elements.button import Button
from pages.base_page import BasePage


class WebTablePage(BasePage):
    """
    Страница регистрации (Registration Page).

    Включает элементы:
    - Форма регистрации
    - Кнопка для перехода на страницу входа
    - Кнопка для отправки формы регистрации

    Наследуется от BasePage.
    """

    def __init__(self, page: Page, settings: Settings):
        """
        Инициализация страницы регистрации.

        :param page: Экземпляр страницы Playwright
        """
        super().__init__(page, settings)

        # Компоненты страницы
        # self.registration_form = RegistrationFormComponent(page)  # Форма регистрации

        # Элементы страницы
        button_locator = self.page.get_by_role("button", name="Add")
        self.add_button = Button(page, locator=button_locator, name="Button [Add]")  #

    def click_add_button(self):
        """
        Клик на кнопку [Add] и проверка перехода на страницу панели управления.

        :raises AssertionError: Если URL не соответствует ожидаемому
        """
        # Нажатие на кнопку регистрации
        self.add_button.click()
        # Проверка, что мы перенаправлены на страницу панели управления
        # self.check_current_url(re.compile(".*/#/dashboard"))