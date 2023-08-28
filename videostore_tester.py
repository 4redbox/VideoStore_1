from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import time
import requests

def validate_video(button, index):

    # Initialize WebDriver for each thread
    options = webdriver.ChromeOptions()
    local_driver = webdriver.Chrome(options=options)
    
    # Note: You might have to navigate to the page where these buttons are present.
    play_button = local_driver.find_elements(By.CLASS_NAME, "play-button")[index]
    play_button.click()
    
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    video_status = ''
    
    try:
        video_element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'customVideo')))
        video_title = driver.find_element(By.CLASS_NAME, "above-video-text").text
        
        if video_element:
            source_element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//video[@id="customVideo"]/source')))
            video_source = source_element.get_attribute('src')
            
            try:
                response = requests.get(video_source, timeout=3)
                print("Checking video: ",video_title)
                if response.status_code == 200:
                    video_status = f"{video_title}: Video is playable."
                else:
                    video_status = f"{video_title}: Video returned {response.status_code}. Video is not playable."
                    
            except Exception as e:
                video_status = f"{video_title}: Could not fetch the video. Error: {e}"
        else:
            video_status = f"{video_title}: Video element not found. Video is not playable."
    except Exception as e:
        video_status = f"An error occurred for video at index {index}: {e}"

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)

    local_driver.quit()

    return video_status

# Read ID and password from a file
try:
    with open("/Users/slver/Documents/CloudTech/VideoStore_1/credentials.txt", "r") as f:
        lines = f.readlines()
        username = lines[0].strip()
        password = lines[1].strip()
except FileNotFoundError:
    print("Credentials file not found. Make sure the file exists.")
    exit(1)

# Initialize WebDriver
try:
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
except Exception as e:
    print(f"Failed to initialize WebDriver: {e}")
    exit(1)

# Open the website
driver.get("https://cloudtechtr.click/signin")

# Assuming username and password fields have input tags with name attributes "username" and "password"
driver.find_element(By.NAME, "username").send_keys(username)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

# Add a sleep to wait for login to complete
time.sleep(2)

# Validate if login was successful
if "<th>Class No</th>" in driver.page_source:
    print("Login successful")
else:
    print("Login failed")
    driver.quit()
    exit(1)

# Wait for page to load and find "play-button"
time.sleep(2)

video_report = []

# Find all "play-buttons"
play_buttons = driver.find_elements(By.CLASS_NAME, "play-button")

# Validate each video in parallel
with ThreadPoolExecutor() as executor:
    for index, button in enumerate(play_buttons):
        print("inside loop")
        video_report.append(executor.submit(validate_video, button, index).result())

# Close the browser
driver.quit()

# Print the report
print("\nVideo Validation Report:")
for report in video_report:
    print(report)