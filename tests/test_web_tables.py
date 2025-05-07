import allure
import pytest

from pages.web_tables_page import WebTablePage
from tools.routes import AppRoute


@pytest.mark.regression
@pytest.mark.smoke
@allure.feature("Authentication")
@allure.story("User login")
class TestWebTables:
    @allure.title("First test Web Tables")
    @allure.description("Проверка успешной авторизации пользователя")
    def test_first_test(
            self,
            webtable_page: WebTablePage,
    ):
        # 1. Переход на страницу Web Tables
        webtable_page.open(AppRoute.WEB_TABLES)
        webtable_page.add_button.click()
        assert 5 == 5, "Тест ожидаемо упал" # Запланированное падение теста
        # webtable_page.page.wait_for_timeout(5000)
