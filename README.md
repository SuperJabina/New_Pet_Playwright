> ⚠️ **Внимание**: Этот README в стадии разработки. Информация может быть неполной или изменяться.

Web Tables Automation Testing
This project provides automated tests for the "Web Tables" page of a web application, focusing on the registration form. The tests validate form input fields, check border colors for error states, and ensure correct form behavior using Playwright, Pytest, and Allure for reporting. The project follows a modular structure with reusable components and test data generation.
Table of Contents

Features
Technologies
Project Structure
Prerequisites
Installation
Running Tests
Generating Allure Reports
Contributing
License

Features

Form Validation: Tests input fields (first_name, last_name, email, age, salary, department) with various test cases (valid, invalid, edge cases).
Border Color Checks: Verifies border-bottom-color for error states (e.g., rgb(220, 53, 69) for invalid inputs).
Dynamic Test Data: Generates test cases using faker and custom data classes (Name, Department, Salary, etc.).
Modular Design: Implements page object model (POM) with components (BaseComponent, RegistrationFormComponent) and elements (Text, Input, Button).
Comprehensive Reporting: Uses Allure for detailed test reports with logs, screenshots, and JSON attachments.
Pytest Parametrization: Supports parameterized tests for multiple fields and test cases.

Technologies

Python: 3.8+
Playwright: Browser automation for end-to-end testing
Pytest: Testing framework with parametrization
Allure-Pytest: Reporting for test results
Faker: Generates realistic test data
Logging: Custom logging for debugging
Typing: Type hints for better code clarity


Prerequisites

Python: 3.8 or higher
Node.js: Required for Playwright browser installation
Git: For cloning the repository
Allure: For generating reports (optional, see Generating Allure Reports)

Installation

Clone the repository:
git clone https://github.com/your-username/web-tables-testing.git
cd web-tables-testing


Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt


Install Playwright browsers:
playwright install



Running Tests

Run all tests:
pytest


Run specific tests (e.g., for first_name field):
pytest -k "first_name"


Run with verbose output and logs:
pytest -s -v


Run smoke tests:
pytest -m smoke


Run regression tests:
pytest -m regression



Tests generate Allure results in the allure-results directory.
Generating Allure Reports

Install Allure (if not installed):

On macOS:brew install allure


On Windows/Linux, follow Allure installation guide.


Generate and serve the report:
allure serve allure-results

This opens a browser with the test report, including logs, screenshots, and JSON attachments.


Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a pull request.

Please ensure your code follows PEP 8 and includes tests.
License
This project is licensed under the MIT License. See the LICENSE file for details.
