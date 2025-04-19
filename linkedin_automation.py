import os
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Retrieve environment variables
EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")
FILE_PATH = os.getenv("FILE_PATH")

# Configure Chrome options for stealth automation
options = uc.ChromeOptions()
# Headless mode can be detectable. If possible, test without headless mode before switching back.
options.add_argument("--headless=new")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--incognito")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

# Initialize the undetected Chrome driver
driver = uc.Chrome(options=options)

def login():
    try:
        driver.get("https://www.linkedin.com/login")
        wait = WebDriverWait(driver, 10)

        # Wait for and fill in email and password fields
        email_elem = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email_elem.send_keys(EMAIL)

        password_elem = driver.find_element(By.ID, "password")
        password_elem.send_keys(PASSWORD)

        # Optionally check/uncheck the "Keep me logged in" checkbox if it appears
        try:
            remember_me = driver.find_element(By.ID, "rememberMeOptIn")
            if remember_me.is_selected():
                driver.execute_script("arguments[0].click();", remember_me)
        except Exception as e:
            print("Checkbox handling skipped:", str(e))

        # Submit the login form
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()

        # Allow a longer time to process the login attempt
        wait = WebDriverWait(driver, 30)
        wait.until(lambda d: "feed" in d.current_url or 
                            "checkpoint" in d.current_url or 
                            "login-submit" in d.current_url)
        current_url = driver.current_url
        print(f"Current URL after login attempt: {current_url}")

        # Detect if LinkedIn security challenge is present
        if "checkpoint/challenge" in current_url:
            print("⚠️ LinkedIn security verification detected! ⚠️")
            screenshot_path = "verification_challenge.png"
            try:
                driver.save_screenshot(screenshot_path)
                print(f"✓ Screenshot saved to {screenshot_path}")
            except Exception as se:
                print("Failed to save verification screenshot:", str(se))
            
            page_source = driver.page_source.lower()
            if "phone" in page_source:
                print("Detected phone verification challenge.")
            elif "email" in page_source:
                print("Detected email verification challenge.")
            elif "captcha" in page_source:
                print("Detected CAPTCHA challenge.")
            return "VERIFICATION_REQUIRED"

        # Additional checks for a successful login
        if (driver.find_elements(By.ID, "global-nav") or 
            driver.find_elements(By.CLASS_NAME, "nav-item") or 
            driver.find_elements(By.XPATH, "//a[contains(@href, '/feed')]")):
            print("Login successful!")
            return True
        else:
            print(f"Login state unclear. Current URL: {current_url}")
            return False

    except Exception as e:
        print("Login process failed, refreshing page and retrying...", str(e))
        print("Current URL:", driver.current_url)
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)
        return False

# Attempt login with a preset maximum number of retries
login_attempts = 0
max_attempts = 3
verification_detected = False

while True:
    result = login()
    if result == "VERIFICATION_REQUIRED":
        verification_detected = True
        print("LinkedIn requires verification which cannot be automated reliably.")
        driver.quit()
        exit(0)
    if result == True:
        break
    login_attempts += 1
    if login_attempts >= max_attempts:
        print(f"Failed to login after {max_attempts} attempts.")
        try:
            screenshot_path = "login_failure.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
        except Exception as ex:
            print("Failed to save screenshot:", str(ex))
        driver.quit()
        exit(1)
    print(f"Attempt {login_attempts} of {max_attempts}")
    time.sleep(5)

def open_application_settings():
    try:
        driver.get("https://www.linkedin.com/jobs/application-settings/?hideTitle=true")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains("application-settings"))
        print("Application settings page opened.")
        return True
    except Exception as e:
        print("Failed to open Application settings page:", str(e))
        return False

# Ensure the application settings page is loaded
while not open_application_settings():
    time.sleep(2)

def upload_cv(file_path):
    try:
        wait = WebDriverWait(driver, 10)
        file_label = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[6]/div[3]/div/div/div/div/div[3]/div[2]/label')
        ))
        file_label.click()
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
    print("File does not exist. Please check the path:", FILE_PATH)

def logout():
    try:
        driver.get("https://www.linkedin.com/m/logout/")
        WebDriverWait(driver, 10).until(EC.url_contains("login"))
        print("Logged out successfully.")
    except Exception as e:
        print("Logout failed:", str(e))

logout()
time.sleep(3)
driver.quit()
