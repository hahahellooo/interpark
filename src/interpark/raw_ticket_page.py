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


def extract_ticket_html():
    # ChromeOptions 객체 생성
    options = Options()
    # Headless 모드 활성화
    options.add_argument("--no-sandbox")  # 추가한 옵션
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # 추가한 옵션
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")

    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 크롤링 대상 URL
    open_page_lists = get_open_page_url(53410, 2)

    num = ''
    crawling_list=[]

    try:
        for page in open_page_lists:
            print(f"{page} 접속 중...")
            driver.get(page)
            num = page.split("groupno=")[1].split("&")[0]
            print(num)

            try:
                WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "notice_detail"))
                )
                print("----------------------------------------------")
                # `notice_detail` 클래스 요소 찾기
                detail_element = driver.find_element(By.CLASS_NAME, "notice_detail")
                print("--------------------------------------")
                # `btn` 클래스 내의 모든 링크 수집
                btn_element = detail_element.find_element(By.CLASS_NAME, "btn")
                a_elements = btn_element.find_elements(By.TAG_NAME, "a")
                print("------------------------------------")
                for a in a_elements:
                    href = a.get_attribute("href")
                    if href and 'http' in href:
                        try:
                            ticket_num = href.split('/')[-1].split('?')[0]  # '/' 뒤 숫자 추출
                            print(f"추출된 숫자: {ticket_num}")
                        except Exception as e:
                            print(f"숫자 추출 실패: {e}")
                            
                        link = a.get_attribute("href")
                        print(f"{href} 접속중...")
                        driver.get(link)

                        window_handles = driver.window_handles
                        # 마지막 창으로 전환
                        driver.switch_to.window(window_handles[-1])

                        print("페이지 로드 완료")

                        try:
                            # id="container" 요소 대기
                            container_selector = "#container"  # CSS Selector: id로 선택
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
                            )
                            print("------------------------------")
                            container = driver.find_element(By.CSS_SELECTOR, container_selector)
                            divs = container.find_elements(By.TAG_NAME, 'div')
                            found = False  # productMain을 찾았는지 확인하기 위한 플래그
                            print("------------------------------")
                            for div in divs:
                                # 각 div의 클래스 속성 확인
                                class_name = div.get_attribute("class")
                                if "productMain" in class_name:  # productMain 클래스가 포함된 경우
                                    product_main = div.get_attribute("outerHTML")
                                    # HTML 추출
                                    production_html = product_main.get_attribute("outerHTML")
                                    print("container 영역 HTML 추출 완료")
                                    print(production_html)
                                # BeautifulSoup으로 HTML 포맷팅
                                soup = BeautifulSoup(production_html, "html.parser")
                                crawling_list.append({"data":soup, "num":ticket_num}) 
                                # 결과 출력
                                print(crawling_list)

                        except:
                            print("container를 찾지 못함")
                    else:
                        print("***************예약하기 버튼이 없습니다.***************")
                        break
                        
            except Exception as e:
                print(f"예매 페이지 정보 크롤링 실패: {e}")
        print(num, ticket_num)
        # return inner_html, container_html

    except Exception as e:
        print(f"{page} 페이지 접속 에러: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":

    # 함수 실행
    extract_ticket_html()

