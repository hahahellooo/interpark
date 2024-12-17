import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def performance_info():
    # 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)

    # 브라우저 사이즈 설정
    driver.set_window_size(1900, 1000)

    # 기본 값 설정
    base_num = 49300
    num = base_num  # 초기값 설정

    # 데이터를 저장할 리스트 초기화
    data_list = []

    while num < base_num + 3:  # 종료 조건: 3페이지만 처리
        try:

            num
            url=f'https://ticket.interpark.com/webzine/paper/TPNoticeView.asp?bbsno=34&pageno=233&stext=&no={num}&groupno={num}&seq=0&KindOfGoods=TICKET&Genre=&sort=WriteDate'
            print(f"{num} 페이지 크롤링 중")
            driver.get(url)

           
            # 딕셔너리로 데이터 초기화
            page_data = {
                "open_page_url": url,
                "poster_url": None,
                "page_number": num,
                "link":None,
                "performance_info": None,
                "info_data": {},
                "artists": []
            }

            try:
                # 이미지 태그가 로드될 때까지 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "detail_top"))
                )

                # 이미지 태그 찾기
                img_info = driver.find_element(By.CLASS_NAME, "info")
                img_element = img_info.find_element(By.TAG_NAME, 'img')
                page_data["poster_url"] = img_element.get_attribute("src")  # `src` 속성 추출
                
            except Exception as e:
                print(f"poster url이 없습니다: {e}")

            try:
            
                # 페이지 로드 대기
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
                            page_data["link"] = link.get_attribute("href")
                    else:
                        print("link가 없습니다")
                        
            except Exception as e:
                print(f"link가 없습니다{e}")
            

            # 페이지 로드 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "introduce"))
            )

            # introduce 클래스 내부 데이터 출력
            try:
                introduce_element = driver.find_element(By.CLASS_NAME, "introduce")
                performance_info = introduce_element.find_element(By.CLASS_NAME, "data").text
                page_data["performance_info"] = performance_info
            except Exception:
                print(f"{num} 페이지: 공연정보를 찾을 수 없습니다")

            # info 데이터 수집
            for i in range(1, 5):
                try:
                    info_elements = driver.find_elements(By.CLASS_NAME, f"info{i}")
                    if len(info_elements) > 1:
                        page_data["info_data"][f"info{i}-1"] = info_elements[0].text
                        page_data["info_data"][f"info{i}-2"] = info_elements[1].text
                    elif len(info_elements) == 1:
                        page_data["info_data"][f"info{i}"] = info_elements[0].text
                except Exception:
                    print(f"{num} 페이지: info{i} 정보를 찾지 못함")
                    break

            # casting 데이터 수집
            try:
                casting_elements = driver.find_element(By.CLASS_NAME, "casting")
                artist_lists = casting_elements.find_elements(By.TAG_NAME, "a")

                for artist_list in artist_lists:
                    span_elements = artist_list.find_elements(By.TAG_NAME, "span")
                    img_elements = artist_list.find_elements(By.TAG_NAME, "img")

                    if span_elements and img_elements:
                        # span 요소에서 아티스트 이름 추출
                        artist_name = span_elements[0].text if span_elements else None
                        # img 요소에서 이미지 URL 추출
                        img_url = img_elements[0].get_attribute("src") if img_elements else None

                        page_data["artists"].append({
                            "name": artist_name,
                            "image_url": img_url
                        })

            except Exception as e:
                print(f"{num} 페이지: 아티스트 정보 가져오기 실패: {e}")

            # 페이지 데이터를 리스트에 추가
            data_list.append(page_data)

        except Exception as e:
            print(f"{num} 페이지 접속 에러: {e}")

        # num 값을 증가시켜 다음 페이지로 이동
        num += 1
        print(f"다음 페이지로 이동: {num}")

    # 드라이버 종료
    driver.quit()

    # 수집한 데이터 출력
    for page in data_list:
        print(page)

performance_info()

