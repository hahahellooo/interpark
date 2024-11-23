from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup  # HTML 포맷팅을 위한 라이브러리
from webdriver_manager.chrome import ChromeDriverManager
import time


def extract_container_html():
    """WebDriver 및 Chrome 옵션 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUI 없이 실행
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Chromedriver 설치 및 WebDriver 초기화
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


    try:
        page = "https://tickets.interpark.com/goods/24016386?"  # 대상 URL
        driver.get(page)
        print(f"{page} 접속 중...")

        # 페이지 로드 완료 대기
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

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
            print(f"{page} 접속 실패 ")

        # HTML 파일로 저장
        with open("formatted_container_output.txt", "w", encoding="utf-8") as file:
            file.write(formatted_html)
            print("txt 저장 완료: formatted_container_output.txt")

    except Exception as e:
        print(f"크롤링 중 에러 발생: {e}")

    finally:
        driver.quit()


# 함수 실행
if __name__ == "__main__":
    extract_container_html()

