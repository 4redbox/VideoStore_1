import requests
from bs4 import BeautifulSoup

# File path for username and password
credentials_file = "credentials.txt"

# Website URL
website_url = "http://cloudtechtr.click/"

# Function to test video links
def test_video_links(session, page_content):
    # Parse the HTML content
    soup = BeautifulSoup(page_content, "html.parser")

    # Find all video links
    video_links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        print("Inside Video Links: ",href)
        if href.endswith(".mp4"):
            video_links.append(href)
            full_url = urljoin(website_url, href)
            print(f"Reading video file: {full_url}")

# Read usernames and passwords from file
credentials = []
with open(credentials_file, "r") as file:
    for line in file:
        username, password = line.strip().split(":")
        credentials.append((username, password))

# Login session
session = requests.Session()

# Check login for each combination
for username, password in credentials:
    # Login request
    login_data = {
        "username": username,
        "password": password
    }
    response = session.post(website_url + "signin", data=login_data)

    # Check if login was successful
    if response.status_code == 200:
        print(f"Login successful for username: {username}")
        test_video_links(session, response.content)
        # Perform any further actions after successful login
    else:
        print(f"Login failed for username: {username}")

# Close the session
session.close()
