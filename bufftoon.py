from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime


options = Options()
options.add_argument('--headless')  
options.add_argument('--no-sandbox') 
options.add_argument('--disable-dev-shm-usage') 


service = ChromeService(ChromeDriverManager().install())


driver = webdriver.Chrome(service=service, options=options)


driver.get("https://bufftoon.plaync.com/tag/ranking?currentType=webtoon")

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "width-box"))
)


scroll_pause_time = 1  
pixels_to_scroll = 200  
max_time_limit = 40  
start_time = time.time()  

while (time.time() - start_time) < max_time_limit:
    old_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script(f"window.scrollBy(0, {pixels_to_scroll});")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == old_height:
        break  


current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "bufftoon"
filename = f"{folder_path}/bufftoon_{current_date}.json"



html_source_updated = driver.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

webtoon_data = []
items = soup.select(".split-item")
for item in items:
    rank = item.select_one(".rank").text.strip() if item.select_one(".rank") else "Rank not found"
    title = item.select_one(".title .text").text.strip() if item.select_one(".title .text") else "Title not found"
    image_tag = item.select_one("img")
    image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else "Image URL not found"

    webtoon_data.append({
        "rank": rank,
        "title": title,
        "imageURL": image_url
    })


with open(filename, 'w', encoding='utf-8') as f:
    json.dump(webtoon_data, f, ensure_ascii=False, indent=4)


driver.quit()
