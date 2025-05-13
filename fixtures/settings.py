import json
from pathlib import Path

import pytest
from _pytest.nodes import Item
import allure
from config import Settings
from tools.logger import get_logger

logger = get_logger(__name__)


def pytest_addoption(parser):
    """Пользовательские опции командной строки"""
    parser.addoption('--browser-name', action='store', default="chromium",
                     choices=("chromium", "firefox", "webkit", "remote_browser"),
                     help="Browser to use for tests: chromium, firefox, webkit, remote_browser")


@pytest.fixture(scope="session")
def settings(request) -> Settings:
    """
    Фикстура создаёт объект с настройками один раз на всю тестовую сессию.

    :param request: Объект pytest для доступа к аргументам командной строки.
    :return: Экземпляр класса Settings с загруженными конфигурациями.
    """
    browser_name = request.config.getoption("--browser-name")
    return Settings.initialize(browser_name=browser_name)

# @pytest.hookimpl(tryfirst=True)
# def pytest_collection_modifyitems(session: pytest.Session, config: pytest.Config, items: list[Item]) -> None:
#     """
#         Хук для модификации идентификаторов тестов (nodeid), добавляя суффикс с именем браузера.
#
#         Выполняется после сбора всех тестов pytest. Добавляет к `nodeid` каждого теста
#         суффикс, указывающий используемый браузер (например, `[chromium]`). Логирование
#         выполняется только в главном процессе, чтобы избежать дублирования в `pytest-xdist`.
#
#         :param session: Объект сессии pytest.
#         :param config: Объект конфигурации pytest.
#         :param items: Список тестовых элементов (Pytest Item).
#         """
#     browser = config.getoption("--browser-name", default="chromium")
#     if browser not in {"chromium", "firefox", "webkit", "remote_browser"}:
#         logger.warning(f"Invalid browser name '{browser}', defaulting to 'chromium'")
#         browser = "chromium"
#     # Логируем только в главном процессе (не в воркерах pytest-xdist)
#     if not config.getoption("--dist") or not hasattr(config, "workerinput"):
#         logger.info(f"Modifying {len(items)} test items in session")
#     for item in items:
#         original_name = item.nodeid
#         item._nodeid = f"{original_name} [{browser}]"
#         if not config.getoption("--dist") or not hasattr(config, "workerinput"):
#             logger.debug(f"Modified nodeid to {item._nodeid}")

# @pytest.fixture
# def attach_test_case_data(request):
#     """
#     Фикстура для прикрепления данных тест-кейса в Allure в формате JSON и логирования шага.
#     Добавляет имя браузера к имени теста.
#     """
#     # Получаем параметры теста
#     field = request.node.callspec.params.get("field")
#     case_name = request.node.callspec.params.get("case_name")
#     test_data = request.node.callspec.params.get("test_data")
#
#     # Распаковываем test_data
#     value, expected_result = test_data if test_data else (None, None)
#
#     # Получаем имя браузера из опции --browser-name
#     browser = request.config.getoption("--browser-name", default="chromium")
#     if browser not in {"chromium", "firefox", "webkit", "remote_browser"}:
#         logger.warning(f"Invalid browser name '{browser}', defaulting to 'chromium'")
#         browser = "chromium"
#
#     # Формируем данные для прикрепления, включая value и browser для отображения
#     data = {
#         "field": field,
#         "case_name": case_name,
#         "value": str(value),
#         "expected_result": expected_result,
#         "browser": browser
#     }
#
#     # Прикрепляем параметры к Allure, исключая value и browser из идентификации
#     if field:
#         allure.dynamic.parameter("field", field)
#     if case_name:
#         allure.dynamic.parameter("case_name", case_name)
#     # value и browser не включаются в allure.dynamic.parameter, чтобы не влиять на historyId
#
#     # Прикрепляем данные как JSON
#     allure.attach(
#         json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
#         name="TestCaseData",
#         attachment_type=allure.attachment_type.JSON
#     )
#
#     # Логируем шаг
#     if field and case_name:
#         with allure.step(f"Validate {field} with {case_name} [{browser}]"):
#             logger.info(f"Test parameters: field={field}, case_name={case_name}, value={value}, expected_result={expected_result}, browser={browser}")
#             yield
#     else:
#         yield

@pytest.hookimpl
def pytest_sessionfinish(session: pytest.Session) -> None:
    """
    Хук для выполнения действий после завершения тестовой сессии.

    Создает файл `executor.json` в директории `allure-results` с метаданными о тестовой
    среде для отображения в отчете Allure. Включает информацию о браузере и среде.

    :param session: Объект сессии pytest.
    """
    executor_data = {
        "name": "Local Execution",
        "type": "local",
        "url": "http://localhost",
        "buildName": "Playwright Tests",
        "buildUrl": "http://localhost/builds",
        "reportName": "Allure Report",
        "reportUrl": "http://localhost/reports"
        }

    allure_results_dir = Path("allure-results")
    try:
        allure_results_dir.mkdir(exist_ok=True)
        with open(allure_results_dir / "executor.json", "w") as f:
            json.dump(executor_data, f, indent=2)
        logger.info(f"Executor data written to {allure_results_dir / 'executor.json'}")
    except Exception as e:
        logger.error(f"Failed to write executor.json: {e}")


