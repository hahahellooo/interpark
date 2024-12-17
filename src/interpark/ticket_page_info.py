import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from open_page_url import get_open_page_url

def transform_raw():

    # 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--headless")  # GUI 없이 실행

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)

    # 브라우저 사이즈 설정
    driver.set_window_size(1900, 1000)

    open_page_lists = get_open_page_url(53479,3)

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
                "hosts": {"link":None,
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

            # casting/description 추출 
            try:
                info1_element = driver.find_element(By.CLASS_NAME, "info1")
                description_element = info1_element.find_element(By.CLASS_NAME, "data")
                ticket_data['description'] = description_element.text.strip()
                info2_element = driver.find_element(By.CLASS_NAME, "info2")
                casting_element = info2_element.find_element(By.CLASS_NAME, "data")
                if "캐스팅" in casting_element.text:
                    ticket_data['casting'] = casting_element.text.strip()
                print("casting/description 추출 완료") 

            except Exception:
                print("casting/description가 없습니다")
                
            # 구매 페이지로 이동 후 공연관련 정보 추출
            if ticket_data['hosts']['link']:
                try:
                    driver.get(ticket_data['hosts']['link'])
                    print(f"{ticket_data['hosts']['link']}로 이동중....")

                    window_handles = driver.window_handles
                    # 마지막 창으로 전환
                    driver.switch_to.window(window_handles[-1])
                
                    try:
                        summaries = driver.find_elements(By.CLASS_NAME, "summary")     
                        for summary in summaries:
                            tagtext_elements = summary.find_elements(By.CLASS_NAME, "prdSection")
                            if tagtext_elements:
                                category_info = tagtext_elements[0].text
                                ticket_data["category"]=category_info.split()[0]
                            li_elements = summary.find_elements(By.TAG_NAME, "li")  # summary에서 li 태그 찾기                         
                            for li in li_elements:
                                text = li.text                
                                if "장소" in text:
                                    place = text.split("장소")[1].strip()
                                    ticket_data['location'] = place.replace(", (자세히)", "").replace("(자세히)", "")               
                                elif "공연기간" in text:
                                    date_range = text.split("공연기간")[1].strip()
                                    if "~" in date_range:
                                        start_date, end_date = date_range.split("~")
                                        ticket_data["start_date"] = start_date.strip()
                                        ticket_data["end_date"] = end_date.strip()
                                    else:
                                        ticket_data["start_date"] = ticket_data["end_date"] = date_range.strip()       
                                elif "공연시간" in text:
                                    ticket_data["running_time"] = text.split("공연시간")[1].strip()
                                elif "관람연령" in text:
                                    ticket_data["rating"] = text.split("관람연령")[1].strip()
                                elif "가격" in text:
                                        ticket_data["price"] = None
                                        break
                        print("공연 관련 정보 추출 완료")
                    except Exception as e:                     
                        print("공연 관련 정보 summay를 찾지 못했습니다.")

                    # show_time 추출
                    try:
                        contents_selector = "#content"  # CSS Selector: id로 선택
                        WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, contents_selector))
                            )
                        contents = driver.find_element(By.CSS_SELECTOR, contents_selector)
                        # # contents = driver.find_element(By.CLASS_NAME, "contents")
                        content_casting= contents.find_element(By.CSS_SELECTOR, ".content.casting")
                        # class="content" 요소 찾기
                        content_element = contents.find_element(By.CLASS_NAME, "content")
                        # content 요소 하위 모든 텍스트 추출
                        content_text = content_element.text
                        split_text = content_text.split("공연시간 정보")
                        
                        if len(split_text) > 1:
                            result = split_text[1].strip() 
                            ticket_data['show_time'] = result
                            print("show_time 추출 완료")

                        try:
                            # contentToggleBtn 클릭
                            toggle_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, ".contentToggleBtn"))
                            )
                            if toggle_button:
                                driver.execute_script("arguments[0].click();", toggle_button)
                                print("버튼 클릭 성공")

                            # castingList가 로드될 때까지 대기
                            content_casting = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".prdContents.detail"))
                            )
                            casting_list = WebDriverWait(content_casting, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".castingList"))
                            )

                            # castingItem 요소들 찾기
                            casting_items = casting_list.find_elements(By.CLASS_NAME, "castingItem")
                            
                            # 각 castingItem에서 데이터 추출
                            for item in casting_items:
                                
                                # castingProfile 하위 img src 추출
                                profile_img_elements = item.find_elements(By.CLASS_NAME, "castingProfile")  # 모든 img 요소 가져오기
                                profile_img_srcs = [img.find_element(By.TAG_NAME, "img").get_attribute("src") for img in profile_img_elements]
                                
                                # castingInfo 하위의 castingActor, castingName 텍스트 추출
                                casting_info = item.find_element(By.CLASS_NAME, "castingInfo")
                                
                                # 모든 배우 이름 가져오기
                                actor_names = casting_info.find_elements(By.CLASS_NAME, "castingActor")
                                actor_texts = [actor_name.text for actor_name in actor_names]
                                
                                # 모든 역할 이름 가져오기
                                role_names = casting_info.find_elements(By.CLASS_NAME, "castingName")
                                role_texts = [role_name.text for role_name in role_names]

                                # 데이터 업데이트
                                for img_src, actor, role in zip(profile_img_srcs, actor_texts, role_texts):
                                    # Casting 정보 업데이트
                                    if ticket_data["casting"] is None:
                                        ticket_data["casting"] = []
                                    ticket_data["casting"].append(f"{actor}:{role}")
                                    
                                    # Artist 정보는 마지막 데이터를 기준으로 업데이트
                                    if ticket_data["artist"] is None:
                                        ticket_data["artist"] = []  # 리스트로 초기화
                                    ticket_data["artist"].append({
                                        "artist_name": actor,
                                        "artist_url": img_src
                                        })
                                    break

                        except Exception as e:
                            print("artist 정보가 없습니다.")

                    except Exception as e:
                        print("데이터 추출 중 오류 발생:", e)

                    try:
                        # 가격 데이터가 있는 영역 찾기
                        info_price_list = driver.find_element(By.CLASS_NAME, "infoPriceList")
                        
                        # 가격 데이터를 저장할 딕셔너리
                        price_list = []

                        li_elements = info_price_list.find_elements(By.TAG_NAME, "li")
                        for li in li_elements:
                            text = li.text.strip()  # li 태그의 텍스트 추출
                            if "원" in text:  # 가격 정보가 포함된 텍스트만 처리
                                price_list.append(text.replace("\n", " "))  # 줄바꿈 제거 후 리스트에 추가

                        # 리스트를 ", "로 연결하여 한 줄로 저장
                        ticket_data['price'] = ", ".join(price_list)
                        print("price 추출 완료")

                    except Exception as e:
                        print("가격 데이터가 없습니다.")

                    except Exception as e:
                        print("가격 데이터를 추출하는 중 오류 발생:", e)
                except Exception as e:
                    print("link가 없습니다.")
                
            data_list.append(ticket_data)

        except Exception as e:
            print(f"{page} 페이지 접속 에러: {e}")

    

    # 드라이버 종료
    driver.quit()

    # 수집한 데이터 출력
    for list in data_list:
        print(list)

transform_raw()



