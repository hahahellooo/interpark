from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_img_src():
    # 브라우저 옵션 설정
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1900, 1000)

    # 크롤링 대상 URL
    url = "https://ticket.interpark.com/webzine/paper/TPNoticeView.asp?bbsno=34&pageno=233&stext=&no=49300&groupno=49300&seq=0&KindOfGoods=TICKET&Genre=&sort=WriteDate"  # 실제 URL로 변경

    try:
        print(f"URL 접속 중: {url}")
        driver.get(url)

        # 이미지 태그가 로드될 때까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "detail_top"))
        )

        # 이미지 태그 찾기
        img_info = driver.find_element(By.CLASS_NAME, "info")
        img_element = img_info.find_element(By.TAG_NAME, 'img')
        img_src = img_element.get_attribute("src")  # `src` 속성 추출

        print(f"추출된 이미지 URL: {img_src}")
        return img_src

    except Exception as e:
        print(f"에러 발생: {e}")

    finally:
        driver.quit()

# 함수 실행
extract_img_src()
