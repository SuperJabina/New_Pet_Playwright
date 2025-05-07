import subprocess
import os
import shutil

"""
Для локального запуска тестов на нескольких браузерах с сохранением истории Allure
"""

# Папки для результатов и отчёта Allure
ALLURE_RESULTS_DIR = "allure-results"
ALLURE_REPORT_DIR = "allure-report"
ALLURE_HISTORY_DIR = os.path.join(ALLURE_REPORT_DIR, "history")
ALLURE_RESULTS_HISTORY_DIR = os.path.join(ALLURE_RESULTS_DIR, "history")

# Путь к allure.cmd (замените на ваш актуальный путь)
ALLURE_EXECUTABLE = r"C:\Users\maxim\AppData\Roaming\npm\allure.cmd"

# Список браузеров для тестирования
browsers = ["webkit"]  # ["chromium", "firefox", "webkit", "remote_browser"]

# Создаём папку allure-results, если она не существует
if not os.path.exists(ALLURE_RESULTS_DIR):
    os.makedirs(ALLURE_RESULTS_DIR)

# Копируем историю из allure-report в allure-results, если она существует
if os.path.exists(ALLURE_HISTORY_DIR):
    if os.path.exists(ALLURE_RESULTS_HISTORY_DIR):
        shutil.rmtree(ALLURE_RESULTS_HISTORY_DIR)  # Удаляем старую историю в allure-results
    shutil.copytree(ALLURE_HISTORY_DIR, ALLURE_RESULTS_HISTORY_DIR)
    print(f"Copied Allure history from {ALLURE_HISTORY_DIR} to {ALLURE_RESULTS_HISTORY_DIR}")

# Запускаем тесты для каждого браузера
for browser in browsers:
    print(f"\n=== Running tests for {browser} ===\n")
    subprocess.run(["pytest", f"--browser-name={browser}"])

# Генерируем отчёт Allure после всех запусков
print("\n=== Generating Allure report ===\n")
subprocess.run([ALLURE_EXECUTABLE, "generate", ALLURE_RESULTS_DIR, "-o", ALLURE_REPORT_DIR, "--clean"])

# Открываем отчёт (опционально)
print("\n=== Opening Allure report ===\n")
subprocess.run([ALLURE_EXECUTABLE, "open", ALLURE_REPORT_DIR])

