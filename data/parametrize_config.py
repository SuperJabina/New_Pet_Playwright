from typing import Type, List, Tuple, Any
from data.field_data import Field, TestCaseData

def get_test_cases(data_class: Type[Field]) -> List[Tuple[str, Any, str]]:
    """
    Извлекает тест-кейсы из класса данных.

    Args:
        data_class (Type[Field]): Класс данных (например, Name, Department, Salary).

    Returns:
        List[Tuple[str, Any, str]]: Список тест-кейсов [(case_name, value, expected_result), ...].
    """
    return data_class.generate_test_case_data().test_cases
