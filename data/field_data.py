from dataclasses import dataclass
from typing import List, Tuple, Any, Optional
from faker import Faker
from tools.logger import get_logger

# Инициализация логгера
logger = get_logger(__name__)

fake = Faker('ru_RU')


@dataclass
class TestCaseData:
    test_cases: List[Tuple[str, Any, str]]


@dataclass
class Field:
    """Базовый класс для тестовых данных полей формы."""

    @staticmethod
    def generate_test_case_data(seed: Optional[int] = None) -> TestCaseData:
        """
        Генерирует базовые тест-кейсы для всех полей.

        Args:
            seed (int, optional): Сид для воспроизводимых данных.

        Returns:
            TestCaseData: Объект с тест-кейсами [(case_name, value, expected_result), ...].
        """
        if seed is not None:
            fake.seed_instance(seed)
        return TestCaseData(test_cases=[
            ("empty", "", "error"),
        ])


@dataclass
class TextField(Field):
    """Базовый класс для текстовых полей."""

    @staticmethod
    def generate_test_case_data(seed: Optional[int] = None) -> TestCaseData:
        """
        Генерирует тест-кейсы для текстовых полей.

        Args:
            seed (int, optional): Сид для воспроизводимых данных.

        Returns:
            TestCaseData: Тест-кейсы для текстового поля.
        """
        if seed is not None:
            fake.seed_instance(seed)
        base_cases = Field.generate_test_case_data(seed).test_cases
        specific_cases = [
            ("two_spaces", "  ", "error"),
            ("max_symbols_256", fake.text(max_nb_chars=256)[:256], "success"),
            ("over_max_symbols", fake.text(max_nb_chars=300)[:257], "error"),
            ("space_middle", f"{fake.word()} {fake.word()}", "success"),
            ("space_last", f"{fake.word()} ", "success"),
            ("space_first", f" {fake.word()}", "success"),
            ("special_symbols", "!@#$%^&*()_+-=[]{}|;:,.<>?", "error"),
            ("script", "<script>alert('test')</script>", "success"),
            ("sql", "admin' AND 1=1 -- ", "success"),
        ]
        return TestCaseData(test_cases=base_cases + specific_cases)


@dataclass
class Name(TextField):
    """Тестовые данные для поля first_name."""

    @staticmethod
    def generate_test_case_data(seed: Optional[int] = None) -> TestCaseData:
        """
        Генерирует тест-кейсы для поля first_name.

        Args:
            seed (int, optional): Сид для воспроизводимых данных.

        Returns:
            TestCaseData: Тест-кейсы для first_name.
        """
        if seed is not None:
            fake.seed_instance(seed)
        # Получаем базовые тест-кейсы
        base_cases = TextField.generate_test_case_data(seed).test_cases
        # Убираем, что не подходит
        # base_cases = [case for case in base_cases if case[0] != "empty"]
        # Определяем специфичные тест-кейсы
        specific_cases = [
            ("valid_with_hyphen", f"{fake.first_name()}-{fake.first_name()}", "success"),
            ("valid_with_apostrophe", "O'Connor", "success")
        ]
        return TestCaseData(test_cases=base_cases + specific_cases)


@dataclass
class Department(TextField):
    """Тестовые данные для поля department."""

    @staticmethod
    def generate_test_case_data(seed: Optional[int] = None) -> TestCaseData:
        """
        Генерирует тест-кейсы для поля department.

        Args:
            seed (int, optional): Сид для воспроизводимых данных.

        Returns:
            TestCaseData: Тест-кейсы для department.
        """
        if seed is not None:
            fake.seed_instance(seed)
        base_cases = TextField.generate_test_case_data(seed).test_cases
        departments = ["IT", "HR", "Finance", "Marketing", "Operations"]
        specific_cases = [
            ("valid_department", fake.random_element(departments), "success"),
            ("valid_long_department", "Research and Development", "success"),
            ("valid_with_hyphen", "IT-Security", "success"),
        ]
        return TestCaseData(test_cases=base_cases + specific_cases)


@dataclass
class NumericField(Field):
    """Базовый класс для числовых полей."""

    @staticmethod
    def generate_test_case_data(seed: Optional[int] = None) -> TestCaseData:
        """
        Генерирует тест-кейсы для числовых полей.

        Args:
            seed (int, optional): Сид для воспроизводимых данных.

        Returns:
            TestCaseData: Тест-кейсы для числового поля.
        """
        if seed is not None:
            fake.seed_instance(seed)
        base_cases = Field.generate_test_case_data(seed).test_cases
        specific_cases = [
            ("1", 1, "success"),
            ("zero", 0, "error"),
            ("negative", fake.random_int(min=-1000, max=-1), "error"),
            ("non_numeric", fake.word(), "error"),
        ]
        return TestCaseData(test_cases=base_cases + specific_cases)


@dataclass
class Salary(NumericField):
    """Тестовые данные для поля salary."""

    @staticmethod
    def generate_test_case_data(seed: Optional[int] = None) -> TestCaseData:
        """
        Генерирует тест-кейсы для поля salary.

        Args:
            seed (int, optional): Сид для воспроизводимых данных.

        Returns:
            TestCaseData: Тест-кейсы для salary.
        """
        if seed is not None:
            fake.seed_instance(seed)
        base_cases = NumericField.generate_test_case_data(seed).test_cases
        specific_cases = [
            ("valid_salary", round(fake.random_number(digits=5, fix_len=False) + fake.random.random(), 2), "success"),
            ("too_large", 12345678910.12345678910, "error"),
        ]
        return TestCaseData(test_cases=base_cases + specific_cases)


@dataclass
class Age(NumericField):
    """Тестовые данные для поля age."""

    @staticmethod
    def generate_test_case_data(seed: Optional[int] = None) -> TestCaseData:
        """
        Генерирует тест-кейсы для поля age.

        Args:
            seed (int, optional): Сид для воспроизводимых данных.

        Returns:
            TestCaseData: Тест-кейсы для age.
        """
        if seed is not None:
            fake.seed_instance(seed)
        base_cases = NumericField.generate_test_case_data(seed).test_cases
        specific_cases = [
            ("-1", -1, "error"),
            ("100", 100, "error"),
            ("99", 99, "error"),
            ("valid_age", fake.random_int(min=18, max=99), "success"),
            ("too_young", fake.random_int(min=0, max=17), "error"),
            ("too_old", fake.random_int(min=101, max=200), "error"),
            ("decimal", 25.5, "error"),
        ]
        return TestCaseData(test_cases=base_cases + specific_cases)


@dataclass
class Email(Field):
    """Тестовые данные для поля email."""

    @staticmethod
    def generate_test_case_data(seed: Optional[int] = None) -> TestCaseData:
        """
        Генерирует тест-кейсы для поля email.

        Args:
            seed (int, optional): Сид для воспроизводимых данных.

        Returns:
            TestCaseData: Тест-кейсы для email.
        """
        if seed is not None:
            fake.seed_instance(seed)
        base_cases = Field.generate_test_case_data(seed).test_cases
        specific_cases = [
            ("valid_email", fake.email(), "success"),
            ("cyrillic", "дом@дом.рф", "success"),
            ("domain without dot", "user@domain", "error"),
            ("too_long", f"{'a' * 200}@{'b' * 50}.com", "error"),
            ("domain without at", "userdomain", "error"),
            ("domain -first", "user@-domain.com", "error"),
            ("name end-", "user-@domain.com", "error"),
            ("script", "<script>alert('test')</script>", "error"),
        ]
        return TestCaseData(test_cases=base_cases + specific_cases)