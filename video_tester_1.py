from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from concurrent.futures import ThreadPoolExecutor

def validate_video(index, username, password):
    local_report = []

    options = webdriver.ChromeOptions()
    local_driver = webdriver.Chrome(options=options)
    
    local_driver.get("https://cloudtechtr.click/signin")
    
    local_driver.find_element(By.NAME, "username").send_keys(username)
    local_driver.find_element(By.NAME, "password").send_keys(password)
    local_driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
    time.sleep(2)

    try:
        play_button = local_driver.find_elements(By.CLASS_NAME, "play-button")[index]
        play_button.click()

        local_driver.switch_to.window(local_driver.window_handles[-1])
        time.sleep(2)
        
        video_element = WebDriverWait(local_driver, 3).until(EC.presence_of_element_located((By.ID, 'customVideo')))
        video_title = local_driver.find_element(By.CLASS_NAME, "above-video-text").text

        if video_element:
            source_element = WebDriverWait(local_driver, 3).until(EC.presence_of_element_located((By.XPATH, '//video[@id="customVideo"]/source')))
            video_source = source_element.get_attribute('src')
            headers = {'Range': 'bytes=0-99'}  # just get the first 100 bytes
            response = requests.get(video_source, headers=headers, timeout=2)
            #print('video source: ', video_source)
            #response = requests.get(video_source, timeout=2)
            if response.status_code == 200 or response.status_code == 206:
                local_report.append(f"{video_title}: Video is playable.")
            else:
                local_report.append(f"{video_title}: Video returned {response.status_code}. Video is not playable.")
        
        else:
            local_report.append(f"{video_title}: Video element not found. Video is not playable.")

    except Exception as e:
        local_report.append(f"An error occurred for video at index {index}: {e}")

    local_driver.quit()
    
    return local_report

# Initialize WebDriver for main thread
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
driver.get("https://cloudtechtr.click/signin")

# Read ID and password from a file
try:
    with open("/Users/slver/Documents/CloudTech/VideoStore_1/credentials.txt", "r") as f:
        lines = f.readlines()
        username = lines[0].strip()
        password = lines[1].strip()
except FileNotFoundError:
    print("Credentials file not found. Make sure the file exists.")
    exit(1)

driver.find_element(By.NAME, "username").send_keys(username)
driver.find_element(By.NAME, "password").send_keys(password)
driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

time.sleep(2)

if "<th>Class No</th>" in driver.page_source:
    print("Login successful")
else:
    print("Login failed")
    driver.quit()
    exit(1)

# Find all play buttons
play_buttons = driver.find_elements(By.CLASS_NAME, "play-button")
driver.quit()

# Validate videos
thread_count = 5  # Adjust the thread count here
with ThreadPoolExecutor(max_workers=thread_count) as executor:
    video_report = list(executor.map(validate_video, range(len(play_buttons)), [username]*len(play_buttons), [password]*len(play_buttons)))

# Flatten the list of lists into a single list
video_report = [report for sublist in video_report for report in sublist]

# Initialize a list to keep track of videos that didn't play
videos_not_played = []

# Print the video report
print("\nVideo Validation Report:")
for report in video_report:
    if "not playable" in report:
        videos_not_played.append(report.split(":")[0].strip())  # Extract the title of the video

# Check if all videos played or not and print summary
if len(videos_not_played) == 0:
    print("All Videos Played.")
else:
    print(f"\nThe following videos did not play:")
    for video in videos_not_played:
        print(video)