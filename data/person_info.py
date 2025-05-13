import json
from dataclasses import dataclass

import allure
from faker import Faker
from typing import Optional, List
import random
from tools.logger import get_logger

# Инициализация логгера
logger = get_logger(__name__)

faker = Faker('ru_RU')

@dataclass
class PersonInfo:
    first_name: str
    last_name: str
    middle_name: Optional[str]
    email: str
    phone: str
    password: str
    password2: str
    address: str
    age: str
    city: str
    company: str
    salary: str
    faker_seed: int

    @staticmethod
    @allure.step("Generate person with seed")
    def generate_person(seed: Optional[int] = None, extended: bool = False) -> 'PersonInfo':
        """
                Генерирует данные пользователя.
        """
        if seed is None:
            seed = random.randint(0, 999999)  # Генерируем случайный seed
            msg = f"Generated seed: {seed}"
            logger.info(msg)
            allure.attach(str(seed), name="Faker seed", attachment_type=allure.attachment_type.TEXT)
        Faker.seed(seed)
        random.seed(seed)  # Синхронизируем random с Faker
        passwd = faker.password(length=10, special_chars=True)
        data = {
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "middle_name": faker.middle_name(),
            "email": faker.email(),
            "phone": faker.phone_number(),
            "password": passwd,
            "password2": passwd,
            "address": faker.address(),
            "age": str(random.randint(10, 99)),
            "city": faker.city(),
            "company": faker.company(),
            "salary": str(random.randint(15000, 180000)),
            "faker_seed": seed,
        }
        person_info = PersonInfo(**data)
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
            name="Faker data",
            attachment_type=allure.attachment_type.JSON
        )

        return person_info

    @staticmethod
    @allure.step("Generate multiple persons")
    def generate_multiple_persons(count: int, seed: Optional[int] = None, extended: bool = False) -> List['PersonInfo']:
        """Генерирует список пользователей с уникальными seed для каждого."""
        persons = []
        for i in range(count):
            current_seed = seed + i if seed is not None else random.randint(0, 999999) + i
            with allure.step(f"Generating person {i + 1} with seed {current_seed}"):
                person = PersonInfo.generate_person(seed=current_seed, extended=extended)
                persons.append(person)
        return persons