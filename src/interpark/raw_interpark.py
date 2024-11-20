from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from open_page_link import get_open_page_url

def extract_html():
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

            # `notice_detail` 클래스 요소가 로드될 때까지 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "notice_detail"))
            )

            # `notice_detail` 클래스 요소 찾기
            notice_detail_element = driver.find_element(By.CLASS_NAME, "notice_detail")

            # 내부 HTML 가져오기
            inner_html = notice_detail_element.get_attribute("outerHTML")

            print("추출된 HTML:")
            print(inner_html)

        return inner_html

    except Exception as e:
        print(f"{page} 페이지 접속 에러: {e}")

    finally:
        driver.quit()

    # 함수 실행
extract_html_content()

 
