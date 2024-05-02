from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
current_date = datetime.now().strftime("%Y-%m-%d")
filename = f"bufftoon_{current_date}.json"
# Chrome 서비스 설정
service = ChromeService(ChromeDriverManager().install())
# Chrome 옵션 설정
options = ChromeOptions()
options.add_argument('--headless')
# Chrome 시작
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://bufftoon.plaync.com/tag/ranking?currentType=webtoon")
WebDriverWait(browser, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "component_wrap"))
)
scroll_pause_time = 1
pixels_to_scroll = 1000
max_time_limit = 40
start_time = time.time()
def scroll_down():
    browser.execute_script(f"window.scrollBy(0, {pixels_to_scroll});")
while (time.time() - start_time) < max_time_limit:
    scroll_down()
    time.sleep(scroll_pause_time)
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == browser.execute_script("return window.pageYOffset + window.innerHeight"):
        break
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')
webtoon_data = []
webtoon_list = soup.select('li.DailyListItem__item--LP6_T')
for webtoon in webtoon_list:
    title_tag = webtoon.select_one('span.ContentTitle__title--e3qXt')
    image_tag = webtoon.select_one('img.Poster__image--d9XTI')
    title = title_tag.text.strip() if title_tag else "Title not found"
    image_url = image_tag['src'] if image_tag else "Image URL not found"
    webtoon_data.append({
        'title': title,
        'image_url': image_url
    })
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(webtoon_data, f, ensure_ascii=False, indent=4)
browser.quit()
print(f"JSON 파일이 저장되었습니다: {filename}")
