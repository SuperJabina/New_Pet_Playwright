from typing import Self, Optional
from tools.logger import get_logger
from pydantic import field_validator
from pydantic.networks import HttpUrl
from pydantic.types import DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path

logger = get_logger(__name__)

class Settings(BaseSettings):
    """
    Класс настроек для проекта, загружаемых из файла .env.

    Использует Pydantic v2 для валидации и парсинга переменных окружения.
    Настройки применяются для конфигурации тестов Playwright, включая выбор браузера,
    URL приложения, директории для артефактов и другие параметры.

    :ivar app_url: Базовый URL приложения (должен быть валидным HTTP/HTTPS URL).
    :ivar headless: Режим без графического интерфейса (True для headless).
    :ivar window_size: Размер окна браузера (ширина и высота в пикселях).
    :ivar slow: Замедление выполнения операций Playwright (в миллисекундах).
    :ivar local: Локаль браузера (например, 'ru-RU').
    :ivar videos_dir: Директория для сохранения видео тестов.
    :ivar tracing_dir: Директория для сохранения трейсов Playwright.
    :ivar screenshots_dir: Директория для сохранения скриншотов упавших тестов.
    :ivar expect_timeout: Таймаут для ожиданий Playwright (в миллисекундах).
    :ivar remote_browser: WebSocket-эндпоинт для удалённого браузера (опционально).
    """

    model_config = SettingsConfigDict(
        env_file='.env',  # Загрузка переменных из файла .env
        env_file_encoding='utf-8',
        env_nested_delimiter='.', # Позволяет использовать вложенные переменные, если потребуется
        extra='ignore' # Игнорировать лишние переменные в .env
    )

    browser_name: str = "chromium"
    app_url: HttpUrl = "https://example.com"  # Значение по умолчанию для отладки
    headless: bool = True
    window_size: dict = {"width": 1920, "height": 1080}
    slow: int = 0
    local: str ='ru-RU'
    videos_dir: DirectoryPath = Path("videos")
    tracing_dir: DirectoryPath = Path("tracing")
    screenshots_dir: DirectoryPath = Path("screenshots")
    expect_timeout: float = 5000
    remote_browser: Optional[str] = None

    @field_validator("videos_dir", "tracing_dir", "screenshots_dir", mode="before")
    def create_directory(cls, v):
        path = Path(v)
        path.mkdir(exist_ok=True)
        return path

    @field_validator("browser_name")
    def validate_browser_name(cls, v):
        valid_browsers = {"chromium", "firefox", "webkit", "remote_browser"}
        if v not in valid_browsers:
            raise ValueError(f"browser_name must be one of {valid_browsers}")
        return v

    def __init__(self, **data):
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Loading .env from: {self.model_config['env_file']}")
        try:
            super().__init__(**data)
            logger.debug(f"Settings initialized: {self.model_dump()}")
        except Exception as e:
            logger.error(f"Failed to initialize Settings: {e}")
            raise

    @classmethod
    def initialize(cls, browser_name: str) -> Self:
        """
            Инициализирует экземпляр Settings с учётом опций командной строки.

            :return: Инициализированный объект Settings
            :raises ValueError: если директории не могут быть созданы или невалидны
        """

        # Инициализируем словарь для параметров
        settings_dict = {'browser_name': browser_name}

        try:
            return cls(**settings_dict)
        except Exception as e:
            logger.error(f"Failed to initialize Settings: {e}")
            raise