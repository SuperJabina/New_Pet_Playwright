from playwright.sync_api import Page


class RegistrationFormComponentsLocators:
    def __init__(self, page: Page):
        self.page = page

        self.TITLE_FORM = self.page.locator("text=Registration Form")
        self.FIRST_NAME_INPUT = self.page.get_by_role("textbox", name="First Name")
        self.LAST_NAME_INPUT = self.page.get_by_role("textbox", name="Last Name")
        self.EMAIL_INPUT = self.page.get_by_role("textbox", name="name@example.com")
        self.AGE_INPUT = self.page.get_by_role("textbox", name="Age")
        self.SALARY_INPUT = self.page.get_by_role("textbox", name="Salary")
        self.DEPARTMENT_INPUT = self.page.get_by_role("textbox", name="Department")
        self.SUBMIT_BUTTON = self.page.get_by_role("button", name="Submit")

