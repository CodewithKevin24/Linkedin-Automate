from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

# ✅ Set up Firefox options
options = Options()
options.binary_location = "/usr/bin/firefox"  # Ensure correct Firefox path

# ✅ Initialize WebDriver
driver = webdriver.Firefox(options=options)
driver.get("https://www.linkedin.com/login")

# ✅ Fetch credentials from GitHub Secrets
EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")
FILE_PATH = os.getenv("FILE_PATH")  # CV File Path

# ✅ Log in
email_input = driver.find_element(By.ID, "username")
email_input.send_keys(EMAIL)

password_input = driver.find_element(By.ID, "password")
password_input.send_keys(PASSWORD)
password_input.send_keys(Keys.RETURN)

time.sleep(5)  # Wait for page to load

# ✅ Navigate to Jobs page
driver.get("https://www.linkedin.com/jobs/")

# ✅ Upload CV (Modify selector based on LinkedIn's UI)
time.sleep(3)
upload_button = driver.find_element(By.XPATH, '//input[@type="file"]')
upload_button.send_keys(FILE_PATH)

time.sleep(5)  # Wait for upload to complete

print("✅ CV uploaded successfully!")

# ✅ Close the browser
driver.quit()
