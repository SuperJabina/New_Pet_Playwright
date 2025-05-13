import uuid
from typing import Generator, Any
import allure
import pytest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from playwright.sync_api import Playwright, Page, expect, Browser, BrowserContext
from config import Settings
from tools.logger import get_logger
from pathlib import Path
from pages.web_tables_page import WebTablePage
from tenacity import retry, stop_after_attempt, wait_fixed
# from page_fixtures.registration_page import RegistrationPage

logger = get_logger(__name__)

# Ключ для хранения результата теста в stash
TEST_RESULT_KEY = pytest.StashKey[str]()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo) -> Generator[None, Any, None]:
    """
    Хук для сохранения результата теста в stash.

    Сохраняет статус теста ('passed', 'failed', 'skipped') в item.stash для использования
    в фикстурах, например, для условного прикрепления видео и скриншотов к Allure.
    Вызывается на этапах 'setup', 'call' и 'teardown' теста, но сохраняет результат
    только для этапа 'call' (основное выполнение теста).

    :param item: Тестовый элемент (Pytest Item, представляющий тест).
    :param call: Информация о вызове теста (CallInfo, содержит этап и результат).
    :yield: Ничего не возвращает, но позволяет Pytest передать управление через outcome.
    """
    outcome = yield
    rep = outcome.get_result()
    # Логируем этап вызова для отладки и устранения предупреждения PyCharm
    logger.debug(f"Hook pytest_runtest_makereport called for {item.nodeid} on phase: {call.when}")
    if rep.when == "call":
        item.stash[TEST_RESULT_KEY] = rep.outcome
        logger.debug(f"Saved test result for {item.nodeid}: {rep.outcome}")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def safe_unlink(video_path: Path) -> None:
    """
    Безопасно удаляет файл с повторными попытками в случае ошибки.

    Использует библиотеку `tenacity` для выполнения до трех попыток удаления файла
    с интервалом в 1 секунду между попытками. Игнорирует ошибки, если файл не существует.

    :param video_path: Путь к файлу, который нужно удалить.
    """
    video_path.unlink(missing_ok=True)


def attach_video_to_allure(video_path: Path) -> None:
    """
    Прикрепляет видеофайл к отчету Allure.

    Проверяет существование файла и прикрепляет его как вложение типа `video/webm`.
    Логирует успешное прикрепление или ошибку.

    :param video_path: Путь к видеофайлу.
    """
    if video_path and video_path.exists():
        try:
            allure.attach.file(
                source=video_path,
                name='auto_video',
                attachment_type='video/webm'
            )
            logger.info(f"Video attached for failed test: {video_path}")
        except Exception as e:
            logger.error(f"Failed to attach video {video_path}: {e}")
    else:
        logger.info(f"No video to attach or video file not found: {video_path}")

@pytest.fixture
def page(playwright: Playwright, settings: Settings, request: pytest.FixtureRequest) -> Generator[Page, None, None]:
    """
    Фикстура для запуска браузера и создания новой страницы с учётом настроек.

    Инициализирует браузер в зависимости от `settings.browser_name` (chromium, firefox, webkit, remote_browser).
    Применяет все параметры из `settings`:
    - `app_url`: Базовый URL для контекста.
    - `headless`: Режим без графического интерфейса (для локальных браузеров; для remote_browser задаётся на сервере).
    - `window_size`: Размер окна браузера.
    - `slow`: Замедление выполнения (для отладки).
    - `local`: Локаль браузера (например, 'ru-RU').
    - `videos_dir`: Директория для сохранения видео.
    - `tracing_dir`: Директория для сохранения трейсов.
    - `screenshots_dir`: Директория для сохранения скриншотов.
    - `expect_timeout`: Таймаут для ожиданий Playwright.

    Включает запись видео и трейсинга (screenshots, snapshots, sources).
    После теста:
    - Сохраняет трейс в `settings.tracing_dir`.
    - Прикрепляет видео и скриншот к Allure только если тест упал (failed).
    - Удаляет видео для успешных или пропущенных тестов.
    - Закрывает контекст и браузер.

    :param playwright: Объект Playwright, предоставляемый pytest-playwright.
    :param settings: Настройки проекта (экземпляр Settings).
    :param request: Объект pytest для доступа к контексту теста (FixtureRequest).
    :yield: Новый объект `Page` для каждого теста.
    :raises ValueError: Если указан неподдерживаемый browser_name или отсутствует ws_endpoint для remote_browser.
    """
    logger.info("Starting page fixture setup")
    # Установка глобального таймаута для ожиданий в Playwright
    expect.set_options(timeout=settings.expect_timeout)

    # Проверка и создание директорий для видео, трейсов и скриншотов
    for directory in (settings.videos_dir, settings.tracing_dir, settings.screenshots_dir):
        try:
            directory.mkdir(exist_ok=True, parents=True)
            logger.debug(f"Directory ensured: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            raise

    # Выбор браузера в зависимости от settings.browser_name
    browser: Browser
    if settings.browser_name == "chromium":
        logger.info(f"Launching Chromium browser (headless={settings.headless})")
        browser = playwright.chromium.launch(
            headless=settings.headless,
            slow_mo=settings.slow
        )
    elif settings.browser_name == "firefox":
        logger.info(f"Launching Firefox browser (headless={settings.headless})")
        browser = playwright.firefox.launch(
            headless=settings.headless,
            slow_mo=settings.slow
        )
    elif settings.browser_name == "webkit":
        logger.info(f"Launching Webkit browser (headless={settings.headless})")
        browser = playwright.webkit.launch(
            headless=settings.headless,
            slow_mo=settings.slow
        )
    elif settings.browser_name == "remote_browser":
        if not hasattr(settings, "remote_browser") or not settings.remote_browser:
            raise ValueError("Missing or invalid ws_endpoint in settings.remote_browser for remote_browser")
        logger.info(f"Connecting to remote browser at {settings.remote_browser} (headless={settings.headless})")
        browser = playwright.chromium.connect(
            ws_endpoint=settings.remote_browser,
            slow_mo=settings.slow,
            timeout=30000  # Таймаут для подключения в миллисекундах
        )
    else:
        raise ValueError(
            f"Unsupported browser: {settings.browser_name}. Supported: chromium, firefox, webkit, remote_browser"
        )

    # Добавляем параметр в Allure
    allure.dynamic.parameter("Browser", browser.browser_type.name) # имя вызванного браузера (в имени
    # теста и Parametrs)
    allure.dynamic.tag(settings.browser_name) # имя браузера из settings в -> tags

    # Создание уникальной директории для видео каждого воркера (для pytest-xdist)
    worker_id = "main"
    if request.config.getoption("--dist") and hasattr(request.config, "workerinput"):
        worker_id = request.config.workerinput.get("workerid", "main")
    video_dir = settings.videos_dir / worker_id
    try:
        video_dir.mkdir(exist_ok=True)
        logger.debug(f"Video directory ensured for worker {worker_id}: {video_dir}")
    except Exception as e:
        logger.error(f"Failed to create video directory {video_dir}: {e}")
        raise

    # Создание контекста браузера с настройками
    context: BrowserContext = browser.new_context(
        base_url=str(settings.app_url),
        viewport=settings.window_size,
        locale=settings.local,
        **({"record_video_dir": video_dir} if settings.video else {}) # добавляем запись видео, если включена в .env
    )
    # Включение трейсинга (снимки экрана, DOM-снапшоты, исходный код)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    logger.info("Browser context created with tracing and video recording")

    # Создание новой страницы
    logger.info("Creating new page")
    page: Page = context.new_page()
    logger.info("New page created")

    try:
        yield page
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        request.node.stash[TEST_RESULT_KEY] = "failed"
        raise
    finally:
        logger.info("Cleaning up page fixture")

    # Сохранение трейсинга
    tracing_file = settings.tracing_dir.joinpath(f'{uuid.uuid4()}.zip')

    # Проверка результата теста
    test_result = request.node.stash.get(TEST_RESULT_KEY, "passed")
    # Логирование случая, когда результат теста не найден
    if test_result == "passed" and TEST_RESULT_KEY not in request.node.stash:
        logger.warning(f"Test result not found for {request.node.nodeid}, assuming 'passed'")

    # Прикрепление видео и скриншота только если тест упал
    if test_result == "failed":
        # Останавливаем и сохраняем трейс только для упавших тестов
        try:
            context.tracing.stop(path=tracing_file)
            allure.attach.file(
                source=tracing_file,
                name='trace',
                attachment_type='application/zip'
            )
            logger.info(f"Trace saved and attached for failed test: {tracing_file}")
        except Exception as e:
            logger.error(f"Failed to save or attach trace {tracing_file}: {e}")

        # Скриншот только для упавших тестов
        screenshot_file = settings.screenshots_dir.joinpath(f'{uuid.uuid4()}.jpeg')
        try:
            page.screenshot(path=screenshot_file,
                            type="jpeg",  # Используем JPEG вместо PNG
                            quality=50,
                            # Устанавливаем качество (0-100), 50 — хороший баланс между размером и качеством
                            full_page=False  # Снимаем только видимую часть страницы
                            )
            allure.attach.file(
                source=screenshot_file,
                name='auto_screenshot',
                attachment_type='image/jpeg'
            )
            logger.info(f"Screenshot saved and attached for failed test: {screenshot_file}")
        except Exception as e:
            logger.error(f"Failed to save or attach screenshot {screenshot_file}: {e}")

        # Прикрепление видео для упавших тестов
        video_path = Path(page.video.path()) if page.video else None
        attach_video_to_allure(video_path)
    else:
        # Для успешных тестов останавливаем трейсинг без сохранения
        try:
            context.tracing.stop()
            logger.info("Tracing stopped without saving for successful test")
        except Exception as e:
            logger.error(f"Failed to stop tracing: {e}")

        # Закрываем страницу перед удалением видео
        try:
            page.close()
            logger.info("Page closed before video deletion")
        except Exception as e:
            logger.error(f"Failed to close page: {e}")

        # Удаление видео для успешных или пропущенных тестов
        video_path = Path(page.video.path()) if page.video else None
        if video_path and video_path.exists():
            try:
                safe_unlink(video_path)
                logger.info(f"Video deleted for successful test: {video_path}")
            except Exception as e:
                logger.error(f"Failed to delete video {video_path}: {e}")
        else:
            logger.info(f"No video to delete or video file not found: {video_path}")

    # Закрытие контекста
    try:
        context.close()
        logger.info("Browser context closed")
    except Exception as e:
        logger.error(f"Failed to close context: {e}")

    # Закрытие браузера
    try:
        browser.close()
        logger.info("Browser closed")
    except Exception as e:
        logger.error(f"Failed to close browser: {e}")

@pytest.fixture
def webtable_page(page: Page) -> WebTablePage:
    """
    Фикстура для инициализации страницы Web Tables.

    :param page: Страница браузера, созданная через фикстуру `page`.
    :param settings: Настройки проекта (экземпляр Settings).
    :return: Объект `WebTablePage` для использования в тестах.
    """
    return WebTablePage(page=page)

# @pytest.fixture
# def registration_page(page: Page, settings: Settings) -> RegistrationPage:
#     """
#     Фикстура для инициализации страницы регистрации.
#
#     :param page: Страница браузера, созданная через фикстуру `page`.
#     :param settings: Настройки проекта (экземпляр Settings).
#     :return: Объект `RegistrationPage` для использования в тестах.
#     """
#     return RegistrationPage(page=page, settings=settings)