from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
import os

# Load environment variables
load_dotenv()
EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")
FILE_PATH = os.getenv("FILE_PATH", r"C:\Users\Sakshi\Desktop\linkedin\Kunal'sCV.pdf")

# Initialize Firefox browser
driver = webdriver.Firefox()

# Open LinkedIn login page
driver.get("https://www.linkedin.com/login")

# Login function
def login():
    try:
        wait = WebDriverWait(driver, 10)

        # Enter email and password
        email = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email.send_keys(EMAIL)

        password = driver.find_element(By.ID, "password")
        password.send_keys(PASSWORD)

        # Uncheck 'Keep me logged in' checkbox
        try:
            keep_me_logged_in = wait.until(EC.presence_of_element_located((By.ID, "rememberMeOptIn")))
            if keep_me_logged_in.is_selected():
                driver.execute_script("arguments[0].click();", keep_me_logged_in)
        except Exception as e:
            print("Checkbox not found or already unchecked.", str(e))

        # Click login button
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()

        # Wait until logged in
        wait.until(EC.url_contains("feed"))
        print("Login successful!")
        return True

    except Exception as e:
        print("Login failed, retrying...", str(e))
        return False

# Attempt login until successful
while not login():
    time.sleep(2)

# Open application settings page
def open_application_settings():
    try:
        driver.get('https://www.linkedin.com/jobs/application-settings/?hideTitle=true')
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains("application-settings"))
        print("Application settings page opened.")
        return True
    except Exception as e:
        print("Failed to open Application settings page:", str(e))
        return False

while not open_application_settings():
    time.sleep(2)

# File upload function
def upload_cv(file_path):
    try:
        wait = WebDriverWait(driver, 10)

        # Click file upload label
        file_label = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[6]/div[3]/div/div/div/div/div[3]/div[2]/label')))
        file_label.click()
        
        # Upload file
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
        time.sleep(2)
        file_input.send_keys(file_path)
        time.sleep(2)

        print(f"File uploaded: {file_path}")

    except Exception as e:
        print("Failed to upload file:", str(e))

if os.path.exists(FILE_PATH):
    upload_cv(FILE_PATH)
else:
    print("File does not exist. Please check the path.")

# Logout function
def logout():
    try:
        driver.get("https://www.linkedin.com/m/logout/")
        WebDriverWait(driver, 10).until(EC.url_contains("login"))
        print("Logged out successfully.")
    except Exception as e:
        print("Logout failed:", str(e))

# Logout
logout()

# Final wait before closing
time.sleep(3)
driver.quit()
