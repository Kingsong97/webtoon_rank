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
filename = f"lezincomics_{current_date}.json"

# Chrome 서비스 설정
service = ChromeService(ChromeDriverManager().install())

# Chrome 옵션 설정
options = ChromeOptions()
options.add_argument('--headless')

# Chrome 시작
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://www.lezhin.com/ko/ranking/detail?genre=_all&type=realtime")

#페이지가 완전히 로드될 때까지 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "lzComic__list"))
)

# 천천히 스크롤 다운
scroll_pause_time = 1  # 1초 대기
pixels_to_scroll = 1000  # 한 번에 스크롤할 픽셀 수
max_time_limit = 40  # 전체 작업 시간 제한 (60초)
start_time = time.time()  # 작업 시작 시간

def scroll_down():
    """현재 위치에서 지정된 픽셀 수만큼 아래로 스크롤"""
    browser.execute_script(f"window.scrollBy(0, {pixels_to_scroll});")

while (time.time() - start_time) < max_time_limit:
    scroll_down()
    time.sleep(scroll_pause_time)
    # 스크롤 이동 후 새로운 높이를 계산
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == browser.execute_script("return window.pageYOffset + window.innerHeight"):
        break  # 페이지 끝에 도달


html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

# 데이터 추출
raking_data = []
tracks = soup.select(".lzComic__item")
for track in tracks:
    rank = track.select_one("strong.lzComic__rank").get_text(strip=True)
    title_element = soup.find('p', class_='lzComic__title')
    title = ''.join(title_element.find_all(text=True, recursive=False)).strip()
    artist = track.select_one(".lzComic__artist").get_text(strip=True)
    category = track.select_one(".lzComic__genre").get_text(strip=True)
    image_url = track.select_one("picture.lzComic__img img").get('srcset')

    raking_data.append({
        "rank": rank,
        "title": title,
        "artist": artist,
        "imageURL": image_url,
        "category": category
    })

  # 데이터를 JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(raking_data, f, ensure_ascii=False, indent=4)

# 브라우저 종료
browser.quit()

print(f"JSON 파일이 저장되었습니다: {filename}")
