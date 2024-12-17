import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 브라우저 꺼짐 방지 옵션
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# 드라이버 생성
driver = webdriver.Chrome(options=chrome_options)

# 브라우저 사이즈 설정
driver.set_window_size(1900, 1000)

# 기본 값 설정
base_num = 49353
num = base_num  # 초기값 설정

while num < base_num + 2:  # 종료 조건: 3페이지만 처리
    try:
        url=f'https://ticket.interpark.com/webzine/paper/TPNoticeView.asp?bbsno=34&pageno=233&stext=&no={num}&groupno={num}&seq=0&KindOfGoods=TICKET&Genre=&sort=WriteDate'
        driver.get(url) 

        print(url)

        # 페이지 로드 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "introduce"))
        )

        # introduce 클래스 내부 데이터 출력
        try:
            introduce_element = driver.find_element(By.CLASS_NAME, "introduce")
            performance_info = introduce_element.find_element(By.CLASS_NAME, "data")
            print(f"{num} 페이지의 공연정보: {performance_info.text}")
        except Exception as e:
            print(f"공연정보를 찾을 수 없습니다")

        for i in range(1, 5):
            try:
                info_elements = driver.find_elements(By.CLASS_NAME, f"info{i}")
                if len(info_elements) > 1:
                    first_info = info_elements[0]
                    second_info = info_elements[1]
                    print(f"info{i}-1번째 정보: ")
                    print(first_info.text)
                    print(f"info{i}-2번째 정보: ")
                    print(second_info.text)

                elif len(info_elements) == 1:
                    print(f"info{i}번째 정보:")
                    print(f'{info_elements[0].text}\n')
                    print(f"info{i}번째 정보 출력 완료\n")

                elif len(info_elements) == 0:
                    print("info 정보 없음")
                    break

            except Exception as e:
                print(f"info를 찾지 못함")
                break

        try:
            # casting 클래스 내부의 모든 a 태그 가져오기
            casting_elements = driver.find_element(By.CLASS_NAME, "casting")
            artist_lists = casting_elements.find_elements(By.TAG_NAME, "a")  # 모든 a 태그 리스트 가져오기

            if not artist_lists:  # a 태그가 없으면 메시지 출력 후 페이지 탐색을 계속
                print(f"{num} 페이지: 아티스트 리스트가 비어 있습니다.")
            else:
                for idx, artist_list in enumerate(artist_lists):
                    # a 태그 내부의 span 태그에서 아티스트 이름 가져오기
                    span_elements = artist_list.find_elements(By.TAG_NAME, "span")
                    img_elements = artist_list.find_elements(By.TAG_NAME, "img")

                    # 조건: 아티스트 이름과 이미지 링크가 모두 있는 경우에만 출력
                    if span_elements and img_elements:
                        artist_name = span_elements[0].text
                        img_url = img_elements[0].get_attribute("src")
                        print(f"아티스트 {idx + 1}: {artist_name}")
                        print(f"이미지 링크: {img_url}")
                    else:
                        # 필요한 정보가 없으면 건너뜀
                        if not span_elements:
                            print(f"{idx + 1}번째 항목: 아티스트 이름 없음.")
                        if not img_elements:
                            print(f"{idx + 1}번째 항목: 이미지 링크 없음.")

        except Exception as e:
            print(f"아티스트 정보 가져오기 실패: {e}")

    except Exception as e:
        print(f"{num} 페이지 접속 에러: {e}")
    
    # num 값을 증가시켜 다음 페이지로 이동
    num += 1
    print(f"다음 페이지로 이동: {num}")

print("페이지 탐색 완료")
