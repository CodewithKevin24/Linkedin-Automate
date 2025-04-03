from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Firefox options for GitHub Actions
options = Options()
options.binary_location = "/usr/bin/firefox"  # GitHub Actions ke liye Firefox path
options.add_argument("--headless")  # Headless mode

# Initialize Firefox browser
driver = webdriver.Firefox(options=options)

# Fetch environment variables and set path
EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")
FILE_PATH = os.getenv("FILE_PATH")  

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
        
        # Uncheck 'Keep me logged in' checkbox if it exists
        try:
            keep_me_logged_in = driver.find_element(By.ID, "rememberMeOptIn")
            if keep_me_logged_in.is_selected():
                driver.execute_script("arguments[0].click();", keep_me_logged_in)
        except Exception as e:
            # Just log but continue, this is not critical
            print("Checkbox handling skipped:", str(e))
        
        # Click login button
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()
        
        # Wait with a longer timeout and multiple possible success conditions
        wait = WebDriverWait(driver, 30)  # Longer timeout
        
        # Check for multiple possible successful login indicators
        try:
            # Check for feed URL
            wait.until(lambda driver: "feed" in driver.current_url or 
                                     "checkpoint" in driver.current_url or 
                                     "login-submit" in driver.current_url)
            
            # Additional verification - check for common elements after login
            if driver.find_elements(By.ID, "global-nav") or \
               driver.find_elements(By.CLASS_NAME, "nav-item") or \
               driver.find_elements(By.XPATH, "//a[contains(@href, '/feed')]"):
                print("Login successful!")
                print("Current URL:", driver.current_url)
                return True
            else:
                current_url = driver.current_url
                print(f"Login may have failed. Current URL: {current_url}")
                if "checkpoint" in current_url:
                    print("LinkedIn is asking for verification. This needs manual intervention.")
                return False
                
        except Exception as e:
            print("Failed to detect login success:", str(e))
            print("Current URL:", driver.current_url)
            return False
            
    except Exception as e:
        print("Login process failed, refreshing page and retrying...", str(e))
        print("Current URL:", driver.current_url)
        # Refresh the page before retrying
        driver.get("https://www.linkedin.com/login")
        time.sleep(3)  # Add a delay before retry
        return False

# Attempt login until successful
login_attempts = 0
max_attempts = 5
while not login():
    login_attempts += 1
    if login_attempts >= max_attempts:
        print(f"Failed to login after {max_attempts} attempts. Exiting.")
        # Take screenshot for debugging
        try:
            screenshot_path = "login_failure.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
        except Exception as e:
            print("Failed to save screenshot:", str(e))
        driver.quit()
        exit(1)
    print(f"Attempt {login_attempts} of {max_attempts}")
    time.sleep(5)  # Longer delay between attempts

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
    print("File does not exist. Please check the path:", FILE_PATH)

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
