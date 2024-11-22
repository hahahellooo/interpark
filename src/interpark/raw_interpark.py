from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from open_page_url import get_open_page_url


def extract_html():
    
    # Selenium 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUI 없이 실행
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1900, 1000)

    # 크롤링 대상 URL
    open_page_lists = get_open_page_url(53300, 1)

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
            print("공지 페이지 크롤링 성공")

            try:
                # 페이지 로드 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "btn"))
                )
                # `btn` 클래스 내의 모든 링크 수집
                btn_element = driver.find_element(By.CLASS_NAME, "btn")
                a_elements = btn_element.find_elements(By.TAG_NAME, "a")

                for a in a_elements:
                    href = a.get_attribute("href")
                    if href and 'http' in href:  # 유효한 URL인지 확인
                        link = a.get_attribute("href")
                        try:
                            driver.get(link)
                            print(f"{link}로 이동중....")

                            # 창 전환
                            window_handles = driver.window_handles
                            driver.switch_to.window(window_handles[-1])

                            WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "contents"))
                            )
                            contents_element = driver.find_element(By.CLASS_NAME, "contents")
                            print("--------------------------------------------")
                            product_main = contents_element.find_element(By.CLASS_NAME, "productMain")
                            print("--------------------------------------------")
                            contents_html = product_main.get_attribute("outerHTML")
                            print(contents_html)
                            break
                            
                        except Exception as e:
                            print("예약 페이지 접속 실패")
            
            except Exception as e:
                            print("link가 없습니다")
                        
     
                #             # 새로운 창으로 전환
                #             window_handles = driver.window_handles
                #             driver.switch_to.window(window_handles[-1])

                #         # `container` 클래스 요소 대기
                #         WebDriverWait(driver, 10).until(
                #             EC.presence_of_element_located((By.CLASS_NAME, "container"))
                #         )
                #         container_element = driver.find_element(By.CLASS_NAME, "container")
                #         print("-----------------------------------------------------------")
                #         container_html = container_element.get_attribute("outerHTML")
                #         break

                #     print("예매 페이지 크롤링 성공")

            
            #     print("추출된 HTML:")
            #     print(inner_html, container_html)

            # return inner_html, container_html

    except Exception as e:
        print(f"{page} 페이지 접속 에러: {e}")

    finally:
        driver.quit()


# 함수 실행
extract_html()

