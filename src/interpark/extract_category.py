import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# 브라우저 옵션 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 드라이버 생성
driver = webdriver.Chrome(options=chrome_options)

# 브라우저 사이즈 설정
driver.set_window_size(1900, 1000)

# 기본 페이지 URL
base_url = "https://ticket.interpark.com/webzine/paper/TPNoticeList.asp?tid1=in_scroll&tid2=ticketopen&tid3=board_main&tid4=board_main"

# 데이터 저장을 위한 리스트 초기화
data_list = []

try:
    # 기본 페이지 접속
    driver.get(base_url)

    # iframe 내부로 전환
    iframe = driver.find_element(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(iframe)

    # 페이지 반복 
    for page in range(1, 3):  
        print(f"{page} 페이지 크롤링 중")

        # tbody 접근
        tbody = driver.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, 'tr')

        # 데이터 추출
        for row in rows:
            try:
                # 카테고리(type) 추출
                category = row.find_element(By.CLASS_NAME, "type").text

                # 제목(subject) 및 링크 추출
                subject = row.find_element(By.CLASS_NAME, "subject")
                subject_text = subject.find_element(By.TAG_NAME, "a").text
                subject_link = subject.find_element(By.TAG_NAME, "a").get_attribute("href")

                # 날짜(date) 추출
                open_date = row.find_element(By.CLASS_NAME, "date").text

                # 딕셔너리 형태로 데이터 저장
                data = {
                    "category": category,
                    "title": subject_text,
                    "link": subject_link,
                    "open_ticket_date": open_date
                }

                # 리스트에 데이터 추가
                data_list.append(data)

            except Exception as inner_e:
                print(f"데이터 추출 중 오류 발생: {inner_e}")

        # 다음 페이지 버튼 클릭
        try:
            # "다음 페이지" 버튼 찾기
            next_button = driver.find_element(By.XPATH, '//img[@alt="다음 페이지"]')
            next_button.click()  # 클릭 이벤트
            time.sleep(2)  # 페이지 로드 대기
        except Exception as e:
            print(f"페이지 이동 중 오류 발생 (마지막 페이지일 가능성): {e}")
            break

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    # 드라이버 종료
    driver.quit()

# 수집한 데이터 출력
for item in data_list:
    print(item)

