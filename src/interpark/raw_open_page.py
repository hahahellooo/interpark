from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup  # HTML 포맷팅을 위한 라이브러리
from webdriver_manager.chrome import ChromeDriverManager
from interpark.open_page_url import get_open_page_url
import time
import os


def extract_open_html():
    # ChromeOptions 객체 생성
    options = Options()
    # Headless 모드 활성화
    options.add_argument("--no-sandbox")  # 추가한 옵션
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # 추가한 옵션
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")

    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 크롤링 대상 URL
    open_page_lists = get_open_page_url(49300, 1)

    # 결과 저장 경로 설정
    save_dir = os.path.join("interpark")
    os.makedirs(save_dir, exist_ok=True)  # 디렉토리 생성 (이미 존재하면 무시)

    try:
        for page in open_page_lists:
            print(f"{page} 접속 중...")
            driver.get(page)

            # URL에서 num 값 추출
            num = page.split("groupno=")[1].split("&")[0]

            # `notice_detail` 클래스 요소가 로드될 때까지 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "notice_detail"))
            )

            # `notice_detail` 클래스 요소 찾기
            notice_detail_element = driver.find_element(By.CLASS_NAME, "notice_detail")
            # 내부 HTML 가져오기
            inner_html = notice_detail_element.get_attribute("outerHTML")
            # BeautifulSoup으로 HTML 포맷팅
            soup = BeautifulSoup(inner_html, "html.parser")
            open_html = soup.prettify()

            # HTML 파일로 저장
            file_name = f"{num}.html"
            file_path = os.path.join(save_dir, file_name)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(open_html)

            print(f"{file_name} 저장 완료!")

    except Exception as e:
                print(f"공지페이지 접속 에러 : {e}")

    finally:
          driver.quit()
                               
# 함수 실행
extract_open_html()

