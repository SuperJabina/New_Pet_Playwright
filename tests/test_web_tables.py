import allure
import pytest
from typing import Any
from data.person_info import PersonInfo
from pages.web_tables_page import WebTablePage
from tools.routes import AppRoute
from data.parametrize_config import get_test_cases
from data.field_data import Name, Department, Salary, Age, Email

@pytest.mark.smoke
@allure.feature("Web Tables")
@allure.story("Registration form")
class TestRegistrationForm:

    # Список тест-кейсов: пары (поле формы, список тест-кейсов для поля)
    # Каждый тест-кейс — кортеж (case_name, value, expected_result)
    TEST_CASES = [
        ("first_name", get_test_cases(Name)),
        # ("department", get_test_cases(Department)),
        # ("salary", get_test_cases(Salary)),
        ("age", get_test_cases(Age)),
        ("email", get_test_cases(Email)),
    ]

    # Списки для параметризации тестов
    PARAM_TEST_CASES = [] # Список параметров для @pytest.mark.parametrize
    PARAM_IDS = []        # Список человекочитаемых идентификаторов для тестов
    TEST_CASES_MAP = {}   # Словарь для быстрого доступа к тест-кейсам по полю
    # Формируем параметры и идентификаторы
    for field, cases in TEST_CASES:
        # Сохраняем тест-кейсы для поля в словарь
        TEST_CASES_MAP[field] = cases
        for case_name, value, expected_result in cases:
            # Добавляем параметры (field, case_name) для параметризации
            PARAM_TEST_CASES.append((field, case_name, expected_result))
            # Формируем идентификатор теста, например, "empty in department"
            PARAM_IDS.append(f"{case_name} in {field}")

    @pytest.mark.regression
    # Задаём шаблон имени теста в Allure, используя параметры field и case_name
    @allure.title("Registration form | Validate field [{field}] with [{case_name}] | [{expected_result}]")
    @allure.description("Проверка валидации формы регистрации")
    # Параметризация теста с использованием field и case_name
    @pytest.mark.parametrize(
        "field, case_name, expected_result",
        PARAM_TEST_CASES,
        ids=PARAM_IDS
    )
    def test_field_validation(self, webtable_page: WebTablePage, person_info: PersonInfo, field: str, case_name:
    str, expected_result: str):
        """
        Проверяет валидацию указанного поля формы значениями из тест-кейса.
        Остальные поля заполняются из PersonInfo.

        Args:
            webtable_page (WebTablePage): Фикстура страницы Web Tables.
            person_info (PersonInfo): Фикстура с данными пользователя.
            field (str): Поле формы для валидации (например, "department").
            case_name (str): Имя тест-кейса (например, "empty").
        """
        # Получаем список тест-кейсов для текущего поля из TEST_CASES_MAP
        cases = self.TEST_CASES_MAP[field]
        # Ищем тест-кейс, у которого case_name совпадает с текущим
        # Возвращает кортеж (case_name, value, expected_result) или None
        test_case = next((case for case in cases if case[0] == case_name), None)
        if not test_case:
            raise ValueError(f"Test case {case_name} not found for field {field}")
        _, value, expected_result = test_case

        # Шаг 1: Открываем страницу Web Tables и нажимаем кнопку добавления
        webtable_page.open(AppRoute.WEB_TABLES)
        webtable_page.page.wait_for_timeout(1000)
        webtable_page.add_button.click()
        # Проверяем видимость формы регистрации
        form_visible = webtable_page.registration_form.check_visible()
        assert form_visible, "Registration form is not visible"

        # Шаг 2: Заполняем форму, используя данные person_info и value для поля field
        filled_text = webtable_page.registration_form.fill_form(person=person_info, field=field, value=str(value))

        result = webtable_page.registration_form.check_text_in_form(filled_text)
        assert result, "The entered text does not match the text in the form"

        # Шаг 3: Отправляем форму
        webtable_page.registration_form.submit_button.click()

        # Проверяем видимость формы регистрации после отправки формы
        form_visible = webtable_page.registration_form.check_visible()
        if expected_result == "success":
            assert not form_visible, "Registration form is visible. Expected: not visible (e.g. Validation ok)"
        else:
            assert form_visible, "Registration form is not visible. Expected: visible (e.g. Validation error)"
            expected_border_color = "rgb(220, 53, 69)"
            webtable_page.registration_form.check_field_border_color(field=field, expected_color=expected_border_color)

        # 4. Проверяем результат валидации
        # if expected_result == "error":
        #     error_message = webtable_page.page.locator(".error-message")
        #     expect(error_message).to_be_visible(timeout=5000)
        # else:
        #     success_message = webtable_page.page.locator(".success-message")
        #     expect(success_message).to_be_visible(timeout=5000)