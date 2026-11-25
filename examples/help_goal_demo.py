# Here are two suggestions for handling scraping data from the
# edge visualizer; I'm going to need to figure out which is
# best for my needs.

# # Option1: use curl cffi to spoof the Chrome handshake
# from curl_cffi import requests

# game_id = "2026020151"
# event_id = "336"
# season = "20262027"

# url = f"https://wsr.nhle.com/sprites/{season}/{game_id}/ev{event_id}.json"

# headers = {
#     "Accept": "application/json, text/plain, */*",
#     "Origin": "https://www.nhl.com",
#     "Referer": f"https://www.nhl.com/ppt-replay/goal/{game_id}/{event_id}/",
#     "Sec-Fetch-Dest": "empty",
#     "Sec-Fetch-Mode": "cors",
#     "Sec-Fetch-Site": "cross-site",
# }

# response = requests.get(url, headers=headers, impersonate="chrome")
# response.raise_for_status()

# tracking_data = response.json()
# print(f"Loaded {len(tracking_data)} frames")

####################################################################
## Option 2 seems to work; I'm probably going to use it - allows  ##
## for the requests library alone to be used (with beautifulsoup) ##
####################################################################
# Option 2: HTML Page + BeautifulSoup Session Flow

# If you want to start at the nhl.com/ppt-replay HTML page 
# (pip install requests beautifulsoup4), this script loads 
# the HTML page to pick up session cookies, parses any <script> 
# tags with BeautifulSoup (in case metadata/links are hydrated 
# in the DOM), and uses the same session to pull the sprite JSON:

import re
import requests
from bs4 import BeautifulSoup

game_id = "2026020151"
event_id = "336"
season = "20262027"

page_url = f"https://www.nhl.com/ppt-replay/goal/{game_id}/{event_id}/"
json_url = f"https://wsr.nhle.com/sprites/{season}/{game_id}/ev{event_id}.json"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
})

# 1. Hit the HTML page first to acquire cookies and verify page metadata
html_resp = session.get(page_url, headers={"Accept": "text/html,application/xhtml+xml"})
html_resp.raise_for_status()

soup = BeautifulSoup(html_resp.text, "html.parser")

# Optional: Check if the HTML embeds a sprite URL inside any inline script tag
for script in soup.find_all("script"):
    if script.string and "wsr.nhle.com/sprites" in script.string:
        match = re.search(r'https://wsr\.nhle\.com/sprites/[^"\']+\.json', script.string)
        if match:
            json_url = match.group(0)
            break

# 2. Fetch the JSON using the HTML page as the Referer
api_headers = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.nhl.com",
    "Referer": page_url,
}

json_resp = session.get(json_url, headers=api_headers)
json_resp.raise_for_status()

tracking_data = json_resp.json()
print(f"Loaded {len(tracking_data)} frames")

# breakpoint()