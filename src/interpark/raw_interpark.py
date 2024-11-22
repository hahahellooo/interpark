from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup 
from open_page_url import get_open_page_url
import time


def extract_html():
    # 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUI 없이 실행
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1900, 1000)

    # 크롤링 대상 URL
    open_page_lists = get_open_page_url(53403, 1)

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
            print("공지 페이지 크롤링 성공")
            print("**************************************************************")

            try:
                # `btn` 클래스 요소 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "btn"))
                )
                # `btn` 클래스 내의 모든 링크 수집
                btn_element = driver.find_element(By.CLASS_NAME, "btn")
                a_elements = btn_element.find_elements(By.TAG_NAME, "a")

                
                for a in a_elements:
                    href = a.get_attribute("href")
                    if href and 'http' in href:
                        link = a.get_attribute("href")
                        print("예매 페이지 접속중...")
                        driver.get(link)

                        window_handles = driver.window_handles
                        # 마지막 창으로 전환
                        driver.switch_to.window(window_handles[-1])

                        # 페이지 로드 완료 대기
                        WebDriverWait(driver, 20).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        print("페이지 로드 완료")

                        try:
                            # id="container" 요소 대기
                            container_selector = "#container"  # CSS Selector: id로 선택
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
                            )
                            container = driver.find_element(By.CSS_SELECTOR, container_selector)

                            # HTML 추출
                            container_html = container.get_attribute("outerHTML")
                            print("container 영역 HTML 추출 완료")

                            # BeautifulSoup으로 HTML 포맷팅
                            soup = BeautifulSoup(container_html, "html.parser")
                            formatted_html = soup.prettify()

                            # 결과 출력
                            print(formatted_html)
                        except:
                            print("container를 찾지 못함")

            except Exception as e:
                print(f"예매 페이지 정보 크롤링 실패: {e}")


        # return inner_html, container_html

    except Exception as e:
        print(f"{page} 페이지 접속 에러: {e}")

    finally:
        driver.quit()


# 함수 실행
extract_html()

