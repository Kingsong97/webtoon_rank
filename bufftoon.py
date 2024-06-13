from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from datetime import datetime
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
import os
# 현재 날짜 설정
current_date = datetime.now().strftime("%Y-%m-%d")
folder_path = "bufftoon"
filename = f"{folder_path}/bufftoon_{current_date}.json"
# 폴더가 없으면 생성
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
# Chrome 서비스 설정
service = ChromeService(ChromeDriverManager().install())
# Chrome 옵션 설정
options = ChromeOptions()
options.add_argument('--headless')  # headless 모드로 설정
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# Chrome 시작
browser = webdriver.Chrome(service=service, options=options)
browser.get("https://bufftoon.plaync.com/tag/ranking?currentType=webtoon")
# 웹툰 데이터 저장할 리스트 초기화
webtoon_data = []
try:
    # "split-item" 요소들 가져오기
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "split-item"))
    )
    # 각 split-item 요소에 대해 반복
    webtoon_elements = browser.find_elements(By.CLASS_NAME, "split-item")
    for index, webtoon_element in enumerate(webtoon_elements):
        try:
            # 요소의 href 속성을 사용하여 링크 가져오기
            webtoon_link = webtoon_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            # 새로운 탭 열기
            browser.execute_script("window.open('');")
            browser.switch_to.window(browser.window_handles[1])
            browser.get(webtoon_link)
            # 새로운 페이지 로딩 대기
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".series-info"))
            )
            # 현재 페이지 소스 가져오기
            detail_page_source = browser.page_source
            # BeautifulSoup으로 파싱
            detail_soup = BeautifulSoup(detail_page_source, 'html.parser')
            # 필요한 정보 추출
            image_tag = detail_soup.select_one('.vertical-thumbnail span.img img')
            title_tag = detail_soup.select_one('.series-info .title')
            author_tags = detail_soup.select('.series-info .author')
            description_tag = detail_soup.select_one('.series-info .description')
            tag_tags = detail_soup.select(".btn-wrap.tags.multi-line.tiny a.btn")
            image_url = image_tag['src'] if image_tag else "Image URL not found"
            title = title_tag.text.strip() if title_tag else "Title not found"
            authors = ", ".join([author.text.strip() for author in author_tags])
            description = description_tag.text.strip() if description_tag else "Description not found"
            tags = ", ".join([tag.text.strip() for tag in tag_tags])
            url = browser.current_url
            # 수집한 정보를 딕셔너리에 추가
            webtoon_data.append({
                'image_url': image_url,
                'title': title,
                'authors': authors,
                'description': description,
                'tags': tags,
                'url': url
            })
            # 현재 탭 닫기
            browser.close()
            # 원래 탭으로 돌아가기
            browser.switch_to.window(browser.window_handles[0])
        except Exception as e:
            print(f"Error processing item {index}: {e}")
            # 현재 탭 닫기
            browser.close()
            # 원래 탭으로 돌아가기
            browser.switch_to.window(browser.window_handles[0])
except Exception as e:
    print(f"Error: {e}")
finally:
    # Chrome 종료
    browser.quit()
    # JSON 파일로 저장
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(webtoon_data, f, ensure_ascii=False, indent=4)
    print(f"JSON 파일이 저장되었습니다: {filename}")
