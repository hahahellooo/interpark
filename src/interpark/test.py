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

    open_page_lists = get_open_page_url(53440,5)

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
            if ticket_data['hosts']['link']:
                try:
                    driver.get(ticket_data['hosts']['link'])
                    print(f"{ticket_data['hosts']['link']}로 이동중....")

                    window_handles = driver.window_handles

                    # 마지막 창으로 전환
                    driver.switch_to.window(window_handles[-1])
                    # try:
                    #     # 팝업창이 로드되었는지 확인
                    #     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "popupWrap")))

                    #     # 닫기 버튼을 클릭
                    #     close_button = WebDriverWait(driver, 10).until(
                    #         EC.element_to_be_clickable((By.CSS_SELECTOR, ".popupCloseBtn.is-bottomBtn"))
                    #     )
                    #     close_button.click()
                    #     print("팝업창 닫기 성공")

                    # except Exception as e:
                    #     print("팝업창 닫기 중 오류 발생:", e)

                        # 단일 class 기준
                    # if wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".popupCloseBtn.is-bottomBtn")))
                    #     print("-----------------------------------------------------")
                    #     button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".popupCloseBtn.is-bottomBtn")))
                    #     button.click()
                    #     print("-----------------------------------------------------")
                    #     try:
                    #         summaries = driver.find_elements(By.CLASS_NAME, "summary")
                    #         for summary in summaries:
                    #             info_items = summary.find_elements(By.CLASS_NAME, "infoItem")
                    #             for item in info_items:
                    #                 info_text = item.find_element(By.CLASS_NAME, "infoText").text
                    #                 print(info_text)
                    #     except Exception as e:
                    #         print("요소 추출 중 오류 발생:", e)
                    # else:

                    #     print("*********************************************")
                    # summary_element=driver.find_element(By.CLASS_NAME, "summary")
                    # setion_element=summary_element.find_element(By.CLASS_NAME, "prdSection")
                    # tagtext_element = summary_element.find_element(By.CLASS_NAME, "tagText")
                    # ticket_data['category'] = tagtext_element.text
                    # infobtn = summary_element.find_element(By.CLASS_NAME, "infoBtn")
                    # ticket_data['location'] = infobtn.text
                
                    try:
                        summaries = driver.find_elements(By.CLASS_NAME, "summary")
                        for summary in summaries:
                            li_elements = summary.find_elements(By.TAG_NAME, "li")  # summary에서 li 태그 찾기
                            for li in li_elements:
                                print(li.text)  # 각 li 태그의 텍스트 출력
                       
                               
                    except Exception as e:
                        print("요소 추출 중 오류 발생:", e)
                except Exception as e:
                            print("link가 없습니다.")
                
            # try:

            #     info1_element = driver.find_element(By.CLASS_NAME, "info1")
            #     description_element = info1_element.find_element(By.CLASS_NAME, "data")
            #     ticket_data['description'] = description_element.text.strip()
            #     info2_element = driver.find_element(By.CLASS_NAME, "info2")
            #     casting_element = info2_element.find_element(By.CLASS_NAME, "data")
            #     ticket_data['casting'] = casting_element.text.strip()
            #     print("casting/description 추출 완료") 

            # except Exception:
            #     print("casting/description가 없습니다")

            # if ticket_data["hosts"]["link"]:
            # #     for host_link in ticket_data["hosts"]["link"]:
            #     try:
            #         print(f"{ticket_data['hosts']['link']} 페이지로 이동 중...")
                
            #         window_handles = driver.window_handles 
            #         driver.switch_to.window(window_handles[-1])
            #         print("티켓 예매 사이트로 전환 완료")

            #         # 새로운 페이지에서 추가 정보 추출
            #         try:
            #             # info 클래스 대기
            #             WebDriverWait(driver, 10).until(
            #                 EC.presence_of_element_located((By.CLASS_NAME, "info"))
            #             )
            #             li_elements = driver.find_elements(By.CLASS_NAME, "infoItem")
            #             print(li_elements.text)

            #             # li 내부의 a 태그에서 텍스트 추출
            #             for li in li_elements:
            #                 try:
            #                     a_element = li.find_element(By.CLASS_NAME, "infoBtn")
            #                     text = a_element.text.strip()  # a 태그의 텍스트 추출
            #                     print(f"추출된 텍스트: {text}")
            #                 except Exception as e:
            #                     print(f"infoBtn에서 텍스트를 가져오는 중 오류 발생: {e}")

                            

            #                 # # 특정 조건 ("장소")에 해당하는 텍스트 추출
            #                 # if "장소" in item_text:
            #                 #     print(f"추출된 장소: {item_text.split(':')[-1].strip()}")  # ":" 기준으로 분리 후 오른쪽 값을 가져옴

            #         except Exception as e:
            #             print("정보 읽기 실패")
                    
                            
                    #     info_element = driver.find_element(By.CLASS_NAME, "info")
                    #     ticket_data['location'] = info_element.find_element(By.CLASS_NAME, "infoBtn").text
                    #     ticket_data['start_date'] = info_element.find_element(By.CLASS_NAME, "infoText")[0]
                    #     ticket_data['end_date'] = info_element.find_element(By.CLASS_NAME, "infoText")[1]
                    #     ticket_data["new_info"] = new_info_element.text.strip()
                    #     print("새로운 정보 추출 완료:")
                    # except Exception as e:
                    #     print(f"새로운 페이지에서 정보 추출 실패: {e}")

            # except Exception as e:
            #     print(f"새로운 페이지로 이동 중 오류 발생: {e}")
            # else:
            #     print("미오픈 티켓: link가 없습니다.")
            #     continue

            data_list.append(ticket_data)

        except Exception as e:
            print(f"{page} 페이지 접속 에러: {e}")

    

    # 드라이버 종료
    driver.quit()

    # 수집한 데이터 출력
    for list in data_list:
        print(list)

transform_raw()



