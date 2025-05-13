import json
from typing import Any

import allure
from playwright.sync_api import Page, expect

from components.base_component import BaseComponent
from locators.registration_form_component_locators import RegistrationFormComponentsLocators
from data.person_info import PersonInfo
from elements.text import Text
from elements.input import Input
from elements.button import Button
from tools.logger import get_logger


logger = get_logger(__name__)


class RegistrationFormComponent(BaseComponent):
    """
    Форма регистрации (Registration Form).

    Включает элементы:
    - Title поле названия формы
    - Поле input First Name
    - Поле input Last Name
    - Поле input Email
    - Поле input Age
    - Поле input Salary
    - Поле input Department
    - Кнопка [Submit] для отправки формы регистрации

    Наследуется от BaseComponent.
    """

    def __init__(self, page: Page):
        """
        Конструктор формы регистрации.

        :param page: Экземпляр страницы Playwright
        """
        super().__init__(page)
        self.locators = RegistrationFormComponentsLocators(page)

        # Элементы формы

        self.title_form = Text(page, locator=self.locators.TITLE_FORM, name="Title of Registration Form")
        self.first_name_input = Input(page, locator=self.locators.FIRST_NAME_INPUT, name="First Name field")
        self.last_name_input = Input(page, locator=self.locators.LAST_NAME_INPUT, name="Last Name field")
        self.email_input = Input(page, locator=self.locators.EMAIL_INPUT, name="email field")
        self.age_input = Input(page, locator=self.locators.AGE_INPUT, name="age field")
        self.salary_input = Input(page, locator=self.locators.SALARY_INPUT, name="salary field")
        self.department_input = Input(page, locator=self.locators.DEPARTMENT_INPUT, name="department field")
        self.submit_button = Button(page, locator=self.locators.SUBMIT_BUTTON, name="submit button")

        self.input_fields = {
            "first_name": self.first_name_input,
            "last_name": self.last_name_input,
            "email": self.email_input,
            "age": self.age_input,
            "salary": self.salary_input,
            "department": self.department_input
        }

    @allure.step("Check registration form is visible")
    def check_visible(self):

        return self.title_form.check_visible()

    @allure.step("Fill form by data from PersonInfo")
    def fill_form(self, person: PersonInfo, field: str = None, value: Any = None)-> dict[str, str]:
        """
        Заполняет указанное поле формы значением для валидации.
        Остальные поля заполняются из PersonInfo.

        Args:
            person: Объект PersonInfo с данными пользователя.
            field: Название поля для валидации (опционально).
            value: Значение для валидации (опционально).

        Returns:
            dict[str, str]: Словарь с введёнными значениями полей.

        Raises:
            ValueError: Если не удалось заполнить форму.
        """
        logger.info(f"Filling form, validating {field or 'all fields'} with value: {value if value is not None else 'default'}")
        filled_text = {}
        values = {
            "first_name": person.first_name,
            "last_name": person.last_name,
            "email": person.email,
            "age": str(person.age),
            "salary": str(person.salary),
            "department": person.company
        }

        try:
            for field_name, input_field in self.input_fields.items():
                if field_name == field and value is not None:
                    input_field.fill(str(value))
                    filled_text[field_name] = str(value)
                else:
                    input_field.fill(values[field_name])
                    filled_text[field_name] = values[field_name]
            logger.debug(f"Filled text: {filled_text}")
            return filled_text
        except Exception as e:
            err = f"Error filling form: {str(e)}"
            logger.error(err)
            allure.attach(err, name="Fill Form Error", attachment_type=allure.attachment_type.TEXT)
            raise ValueError(err) from e

    @allure.step("Get CSS property border-bottom-color")
    def get_colors_of_border_fields(self)-> dict[str, str]:
        """
                Получает цвета нижнего бордера для всех полей ввода формы.

                Returns:
                    dict[str, str]: Словарь с именами полей и значениями свойства border-bottom-color.
                                   Например: {"first_name": "rgb(255, 0, 0)", "email": "rgb(0, 128, 0)"}

                Raises:
                    ValueError: Если не удалось получить цвет для одного из полей.
                """
        step = "Getting CSS property border-bottom-color"
        with allure.step(step):
            # Список полей ввода (имя поля соответствует fill_form)
            border_colors = {}
            for field_name, field in self.input_fields.items():
                try:
                    color = field.get_css_property("border-bottom-color")
                    border_colors[field_name] = color
                    logger.info(f"Color bottom-border '{field_name}': {color}")
                except Exception as e:
                    err = f"error getting CSS property '{field_name}': {str(e)}"
                    logger.error(err)
                    raise ValueError(err) from e

            logger.info(f"Border colors retrieved: {border_colors}")
            allure.attach(
                json.dumps(border_colors, indent=2),
                name="Border Colors",
                attachment_type=allure.attachment_type.JSON
            )
            return border_colors

    @allure.step("Check {field} has border color {expected_color}")
    def check_field_border_color(self, field: str, expected_color: str) -> None:
        """
        Проверяет, что указанное поле имеет ожидаемый цвет бордера.

        Args:
            field (str): Имя поля (например, "first_name").
            expected_color (str): Ожидаемый цвет бордера (например, "rgb(220, 53, 69)").

        Raises:
            AssertionError: Если цвет бордера не соответствует ожидаемому.
            ValueError: Если поле не найдено или не удалось получить цвет.
        """
        try:
            color = self.input_fields[field].get_css_property("border-bottom-color")
            assert color == expected_color, f"Border color of {field} is {color}, expected {expected_color}"
            result = "Actual color: {color} = Expected color: {expected_color}"
            logger.info(result)
            allure.attach(
                result,
                name=f"Border Color ({field})",
                attachment_type=allure.attachment_type.TEXT
            )
        except (ValueError, AssertionError) as e:
            logger.error(f"Failed to check border color for '{field}': {str(e)}")
            allure.attach(
                str(e),
                name=f"Border color Check Failure ({field})",
                attachment_type=allure.attachment_type.TEXT
            )
            raise

    @allure.step("Check visible text in form")
    def check_text_in_form(self, filled_text: dict[str, str]) -> bool:
        """
        Проверяет, что значения полей формы соответствуют ожидаемым.

        Args:
            filled_text: Словарь с ожидаемыми значениями полей.

        Raises:
            ValueError: Если поле отсутствует в filled_text или не удалось проверить.
            AssertionError: Если значения не совпадают.
        """


        for field_name, input_field in self.input_fields.items():
            if field_name not in filled_text:
                raise ValueError(f"Field '{field_name}' not found in filled_text")
            expected_value = filled_text[field_name]
            logger.info(f"Checking {field_name} has {expected_value}")
            try:
                if field_name == "email":
                    input_field.check_have_value(expected_value)
                elif field_name == "age":
                    input_field.check_have_value(expected_value[:2])
                elif field_name == "salary":
                    input_field.check_have_value(expected_value[:10])
                else:
                    input_field.check_have_value(expected_value[:25])
            except Exception as e:
                err = f"Error checking field {field_name}: {str(e)}"
                logger.error(err)
                allure.attach(err, name=f"Check Error ({field_name})", attachment_type=allure.attachment_type.TEXT)
                return False
        return True










