import pytest
from playwright.sync_api import Page
from data.person_info import PersonInfo
from data.field_data import TextField
# from data.incincorrect_email_data import IncorrectEmailData

@pytest.fixture
def person_info():
    """Фикстура для генерации корректных данных пользователя."""
    return PersonInfo.generate_person()

# @pytest.fixture
# def text_field_data():
#     """Фикстура для генерации данных валидации текстового поля."""
#     return TextFieldData.generate_text_field_data()

# @pytest.fixture
# def incorrect_texts():
#     """Фикстура для генерации некорректных текстовых данных."""
#     return IncorrectTextData.generate_incorrect_texts()
#
# @pytest.fixture
# def incorrect_emails():
#     """Фикстура для генерации некорректных email."""
#     return IncorrectEmailData.generate_incorrect_emails()