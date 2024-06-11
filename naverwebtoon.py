from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions

# 현재 날짜 설정
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "naverwebtoon"
filename = f"{folder_path}/naverwebtoon_{current_date}.json"

# Chrome 서비스 설정
service = ChromeService(ChromeDriverManager().install())

# Chrome 옵션 설정
options = ChromeOptions()
# options.add_argument('--headless')  # 이 줄을 주석 처리하여 headless 모드를 끕니다.

# Chrome 시작
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://comic.naver.com/webtoon")

# 페이지 요소 로딩 대기
WebDriverWait(browser, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "component_wrap"))
)

# # 페이지 스크롤
# scroll_pause_time = 1  
# pixels_to_scroll = 1000 
# max_time_limit = 40  
# start_time = time.time()  

# def scroll_down():
#     browser.execute_script(f"window.scrollBy(0, {pixels_to_scroll});")

# while (time.time() - start_time) < max_time_limit:
#     scroll_down()
#     time.sleep(scroll_pause_time)

#     new_height = browser.execute_script("return document.body.scrollHeight")
#     if new_height == browser.execute_script("return window.pageYOffset + window.innerHeight"):
#         break  

# HTML 소스 코드 가져오기 및 파싱
html_source_updated = browser.page_source
soup = BeautifulSoup(html_source_updated, 'html.parser')

webtoon_data = []
webtoon_list = soup.find_all('li', class_='DailyListItem__item--LP6_T')

for index in range(len(webtoon_list)):
    try:

         # 각 웹툰 항목 클릭 전, Poster__icon_bullet--D4lUU 클래스 확인
        webtoons = browser.find_elements(By.CLASS_NAME, 'DailyListItem__item--LP6_T')
        bullet_icon = webtoons[index].find_elements(By.CLASS_NAME, 'Poster__icon_bullet--D4lUU')
        
        if bullet_icon:
            print(f"Bullet icon detected for item {index}, skipping...")
            continue
     
        webtoons[index].click()
        
        # 새로운 페이지 로딩 대기
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "EpisodeListInfo__comic_info--yRAu0"))
        )

        # 새로운 페이지 소스 코드 가져오기 및 파싱
        detail_page_source = browser.page_source
        detail_soup = BeautifulSoup(detail_page_source, 'html.parser')
        
        # 필요한 정보 추출
        title_tag = detail_soup.select_one('h2.EpisodeListInfo__title--mYLjC')
        image_tag = detail_soup.select_one('img.Poster__image--d9XTI')
        author_tags = detail_soup.select('span.ContentMetaInfo__category--WwrCp > a.ContentMetaInfo__link--xTtO6')
        weekday_age_tag = detail_soup.select_one('em.ContentMetaInfo__info_item--utGrf')
        description_tag = detail_soup.select_one('p.EpisodeListInfo__summary--Jd1WG')
        tag_tags = detail_soup.select('div.TagGroup__tag_group--uUJza > a.TagGroup__tag--xu0OH')
        
        title = title_tag.text.strip() if title_tag else "Title not found"
        image_url = image_tag['src'] if image_tag else "Image URL not found"
        authors = ", ".join([author.text.strip() for author in author_tags])
        weekday_age = weekday_age_tag.text.strip() if weekday_age_tag else "Weekday and Age not found"
        description = description_tag.text.strip() if description_tag else "Description not found"
        tags = ", ".join([tag.text.strip() for tag in tag_tags])
        url = browser.current_url

        # 요일과 나이를 분리
        if '∙' in weekday_age:
            parts = weekday_age.split('∙')
            weekday = parts[0].strip()
            age = parts[1].strip()
        else:
            weekday = weekday_age
            age = "Age not found"

        webtoon_data.append({
            'title': title,
            'image_url': image_url,
            'authors': authors,
            'weekday': weekday,
            'age': age,
            'description': description,
            'tags': tags,
            'url': url
        })
        
        # 이전 페이지로 돌아가기
        browser.back()
        
        # 다음 항목이 로드될 때까지 대기
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "DailyListItem__item--LP6_T"))
        )
        
        # 현재 항목 위치로 스크롤
        scroll_position = (index + 1) * 100
        browser.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(1)
    except Exception as e:
        print(f"Error processing item {index}: {e}")

# JSON 파일로 저장
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(webtoon_data, f, ensure_ascii=False, indent=4)

browser.quit()

print(f"JSON 파일이 저장되었습니다: {filename}")