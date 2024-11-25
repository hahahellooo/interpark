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


def extract_html():
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

    # 결과 저장 변수 초기화
    inner_html = None
    container_html = None

    try:
        for page in open_page_lists:
            print(f"{page} 접속 중...")
            driver.get(page)

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

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "btn"))
                )

                # `btn` 클래스 내의 모든 링크 수집
                btn_element = driver.find_element(By.CLASS_NAME, "btn")
                links = btn_element.find_elements(By.TAG_NAME, "a")

                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        if 'http' in href:  # 유효한 URL인지 확인
                            print(f"{href} 접속중...")
                            driver.get(href)
                        
                            # 창 전환 처리
                            window_handles = driver.window_handles
                            driver.switch_to.window(window_handles[-1])

                            try:
                                # id="container" 요소 대기
                                container_selector = "#container"
                                WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
                                )
                                container = driver.find_element(By.CSS_SELECTOR, container_selector)
                                divs = container.find_elements(By.TAG_NAME,'div')
                                for div in divs:
                                     class_name = div.get_attribute("class")
                                     if "productMain" in class_name:
                                        product_main_html = div.get_attribute("outerHTML")

                                        # BeautifulSoup으로 HTML 포맷팅
                                        soup = BeautifulSoup(product_main_html, "html.parser")
                                        formatted_html = soup.prettify()

                                        # 결과 출력
                                        print(formatted_html)

                            except Exception as inner_e:
                                print(f"container 또는 productionMain을 찾지 못함: {inner_e}")
                                continue  # 다음 링크로 넘어감

                    else:
                        print("***************예약하기 버튼이 없습니다.***************")
                        continue
                
            except Exception as e:
                print(f"예매 페이지 정보 크롤링 실패: {e}")

        return inner_html, formatted_html
    except Exception as e:
                print(f"공지페이지 접속 에러 : {e}")
                               
# 함수 실행
extract_html()

