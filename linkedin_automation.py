from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Firefox options for GitHub Actions
options = Options()
options.binary_location = "/usr/bin/firefox"  # Firefox ka path GitHub Actions ke liye
options.add_argument("--headless")  # Headless mode for faster execution

# Initialize Firefox WebDriver
try:
    driver = webdriver.Firefox(options=options)
    print("WebDriver started successfully")
except Exception as e:
    print(f"WebDriver failed to start: {str(e)}")
    raise

# Fetch environment variables from GitHub Secrets
EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")
WORKSPACE = os.getenv("GITHUB_WORKSPACE", "")  # GitHub Actions workspace
FILE_PATH = os.path.join(WORKSPACE, os.getenv("FILE_PATH", "cv.pdf"))  # Absolute path for CV

# Open LinkedIn login page
driver.get("https://www.linkedin.com/login")
print("LinkedIn login page opened")

# Login function
def login():
    try:
        wait = WebDriverWait(driver, 10)

        # Enter email
        email = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email.send_keys(EMAIL)
        print("Email entered")

        # Enter password
        password = driver.find_element(By.ID, "password")
        password.send_keys(PASSWORD)

        # Submit login
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()
        print("Login button clicked")

        # Check if login worked or email link sent
        time.sleep(5)  # Wait for redirect or email link page
        if "feed" in driver.current_url:
            print("Login successful!")
            return True
        elif "checkpoint" in driver.current_url or "email" in driver.current_url:
            print("LinkedIn sent a one-time email link. Please manually click the link in your email to complete login.")
            print("After clicking the link, wait for the script to proceed.")
            wait.until(EC.url_contains("feed"), message="Manual email link click required. Timeout after 5 mins.")
            print("Login completed after email link!")
            return True
        else:
            print("Login failed: Unknown page")
            return False

    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False

# Attempt login
while not login():
    print("Retrying login...")
    time.sleep(2)

# Open application settings page
def open_application_settings():
    try:
        driver.get("https://www.linkedin.com/jobs/application-settings/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains("application-settings"))
        print("Application settings page opened")
        return True
    except Exception as e:
        print(f"Failed to open settings page: {str(e)}")
        return False

while not open_application_settings():
    time.sleep(2)

# File upload function
def upload_cv(file_path):
    try:
        wait = WebDriverWait(driver, 10)

        # Find file input (updated XPath based on LinkedIn's current UI)
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
        file_input.send_keys(file_path)
        time.sleep(3)  # Wait for upload to process
        print(f"CV uploaded successfully: {file_path}")
    except Exception as e:
        print(f"Failed to upload CV: {str(e)}")

# Check if file exists and upload
if os.path.exists(FILE_PATH):
    upload_cv(FILE_PATH)
else:
    print(f"File not found at: {FILE_PATH}")

# Logout function
def logout():
    try:
        driver.get("https://www.linkedin.com/m/logout/")
        WebDriverWait(driver, 10).until(EC.url_contains("login"))
        print("Logged out successfully")
    except Exception as e:
        print(f"Logout failed: {str(e)}")

# Logout
logout()

# Close browser
time.sleep(2)
driver.quit()
print("Browser closed")
