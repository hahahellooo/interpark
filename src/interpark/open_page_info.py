import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from open_page_url import get_open_page_url

def transform_raw():

    # 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)

    # 브라우저 사이즈 설정
    driver.set_window_size(1900, 1000)

    open_page_lists = get_open_page_url(53550,5)

    # 데이터를 저장할 리스트 초기화
    data_list = []
    
    for page in open_page_lists:
        try:
            print(f"{page} 접속 중")
            driver.get(page)
       
            # 딕셔너리 초기화 
            ticket_data = {
                "title":None,
                "category":None,
                "location":None,
                "price":None,
                "start_date":None,
                "end_date":None,
                "show_time":None,
                "running_time":None,
                "casting": None,
                "rating": None,
                "description":None,
                "poster_url": None,
                "open_date":None,
                "pre_open_date": None,
                "artist": None,
                "artist_url": None,
                "hosts": {"host_name":"interpark",
                        "link":None,
                        "site_id":1}
            }

            # post_url 가져오기
            try:
                # 이미지 태그가 로드될 때까지 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "detail_top"))
                )
                # 이미지 태그 찾기
                img_info = driver.find_element(By.CLASS_NAME, "info")
                img_element = img_info.find_element(By.TAG_NAME, 'img')
                ticket_data["poster_url"] = img_element.get_attribute("src")  # `src` 속성 추출
                ticket_data["title"] = driver.find_element(By.TAG_NAME, 'h3').text
                ticket_data["open_date"] = driver.find_element(By.CLASS_NAME, "open").text.split("\n")[1]
                li_elements = driver.find_elements(By.TAG_NAME, "li")
                for li in li_elements:
                    if "선예매" in li.text:
                        ticket_data["pre_open_date"] = li.text.split("\n")[1]
                        break  # 원하는 정보를 찾으면 반복문 종료
                print("title/pre_open_date/open_date/poster_url 추출 완료")
            
            except Exception as e:
                print(f"poster_url이 없습니다")

            # 티켓 판매 link 가져오기
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
                        ticket_data["hosts"]["link"] = a.get_attribute("href")
                        break
                print("link 추출 완료")

            except Exception as e:
                print(f"link가 없습니다")
                
            # introduce 클래스 내부 데이터 출력 - casting/description
            if not ticket_data["hosts"]["link"]:
                try:
                    introduce_element = driver.find_element(By.CLASS_NAME,"introduce")
                    detail_element = introduce_element.find_element(By.CLASS_NAME, "data")
                    detail_text = detail_element.find_element(By.TAG_NAME,"p").text
                    lines = detail_text.strip().split("\n")  # 줄 단위로 나누기
                    print(lines)

                    for line in lines:
                        line = line.replace(" ", "").strip()  # 모든 공백 제거
                        if "뮤지컬" in line or "연극" in line:
                            ticket_data["category"] = "뮤지컬/연극"
                        elif "공연기간" in line or "공연일시" in line:  # 수정된 조건
                            date = line.split(":")[1].split("~")  # ':' 이후를 가져오고 '~' 기준으로 분리
                            ticket_data["start_date"] = date[0].strip()
                            ticket_data["end_date"] = date[1].strip()
                        elif "공연시간" in line:
                            ticket_data["show_time"] = line.split(":")[1].strip()
                        elif "공연장" in line or "관람장소" in line or "공연장소" in line:  # 수정된 조건
                            ticket_data["location"] = line.split(":")[1].strip()
                        elif "러닝타임" in line:
                            ticket_data["running_time"] = line.split(":")[1].strip()
                        elif "관람연령" in line or "관람등급" in line:  # 수정된 조건
                            ticket_data["rating"] = line.split(":")[1].strip()
                        elif "티켓가격" in line or "가격" in line or "티켓가" in line:  # 수정된 조건
                            ticket_data["price"] = line.split(":")[1].strip()
                                            
                        else:
                            print("실패 !!!!!!!!!!!!!!!!!!")
                            break
                except Exception:
                    print("공연정보가 없습니다")
                
                try:

                    info1_element = driver.find_element(By.CLASS_NAME, "info1")
                    description_element = info1_element.find_element(By.CLASS_NAME, "data")
                    ticket_data['description'] = description_element.text.strip()
                    info2_element = driver.find_element(By.CLASS_NAME, "info2")
                    casting_element = info2_element.find_element(By.CLASS_NAME, "data")
                    ticket_data['casting'] = casting_element.text.strip()
                    print("casting/description 추출 완료") 

                except Exception:
                    print("casting/description가 없습니다")

            data_list.append(ticket_data)

        except Exception as e:
            print(f"{page} 페이지 접속 에러: {e}")

    

    # 드라이버 종료
    driver.quit()

    # 수집한 데이터 출력
    for list in data_list:
        print(list)

transform_raw()

