from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from open_page_link import get_open_page_url


# 브라우저 꺼짐 방지 옵션
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 드라이버 생성
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1900, 1000)

# 크롤링 대상 URL
open_page_lists = get_open_page_url(53378,3)

# 저장할 때 open_page_url도 상단에 저장하도록 설정

try:
    for page in open_page_lists:
            print(f"{page} 접속 중")
            driver.get(page)
        casting_elements = driver.find_element(By.CLASS_NAME, "casting")
        artist_lists = casting_elements.find_elements(By.TAG_NAME, "a")

        # 아티스트와 URL을 저장할 리스트 초기화
        ticket_data["artists"] = []  # 아티스트 이름 리스트
        ticket_data["artist_urls"] = []  # 아티스트 이미지 URL 리스트

        for artist_list in artist_lists:
            span_elements = artist_list.find_elements(By.TAG_NAME, "span")
            img_elements = artist_list.find_elements(By.TAG_NAME, "img")

            artist_name = None
            artist_url = None

            # span 요소에서 아티스트 이름 추출
            if span_elements:
                artist_name = span_elements[0].text

            # img 요소에서 이미지 URL 추출
            if img_elements:
                artist_url = img_elements[0].get_attribute("src")

            # 아티스트 이름과 URL을 리스트에 추가
            if artist_name or artist_url:
                ticket_data["artists"].append(artist_name if artist_name else "Unknown Artist")
                ticket_data["artist_urls"].append(artist_url if artist_url else "Unknown URL")

        print("artist/artist_url 추출 완료:")
        print("아티스트 이름 리스트:", ticket_data["artists"])
        print("아티스트 URL 리스트:", ticket_data["artist_urls"])

    except Exception as e:
        print(f"artist/artist_url 정보를 가져오는 중 에러 발생: {e}")
