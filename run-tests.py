import subprocess
"""
Для локального запуска тестов на нескольких браузерах
"""
browsers = ["chromium"] # ["chromium", "firefox", "webkit", "remote_browser"]

for browser in browsers:
    print(f"\n=== Running tests for {browser} ===\n")
    subprocess.run(["pytest", f"--browser-name={browser}"])