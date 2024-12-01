from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from bs4 import BeautifulSoup

def html_parsing():
    aws_conn_id = 'interpark'  # Airflow 연결 ID
    bucket_name = 't1-tu-data'

    hook= S3Hook(aws_conn_id=aws_conn_id)

    # 처리할 파일 번호 (예: 49609부터 시작)
    #base_file_number = 49609
    base_file_number = 53327
    # 파일 번호를 하나씩 증가시키면서 반복 처리
    while True:
        # '49609_'로 시작하는 파일 리스트를 가져옵니다.
        s3_key_prefix = f'interpark/{base_file_number}'
        files = hook.list_keys(bucket_name, prefix=s3_key_prefix)

        found_base_file_number_ = None
        for file in files:
            if file.startswith(f'interpark/{base_file_number}_'):
                found_base_file_number_ = file
                break  # 첫 번째로 발견된 '49609_' 파일을 우선 처리

        # '49609_'로 시작하는 파일이 있으면 이를 먼저 처리
        if found_base_file_number_:
            print(f"Processing {found_base_file_number_}")
            file_html = hook.read_key(found_base_file_number_, bucket_name)
            soup = BeautifulSoup(file_html, 'html.parser')

             # 카테고리 (뮤지컬 등)
            category = soup.find('div', class_='tagText')
            if category:
                category_text = category.find_all('span')[0].text.strip()
                if not any(keyword in category_text for keyword in ["뮤지컬", "연극", "전시/행사", "콘서트"]):
                    print(f"{category_text}는 넘어갑니다.")
                    base_file_number+=1
                    continue
            

            # ticket_data 구조 정의
            ticket_data = {
                "title": None,
                "category": None,
                "location": None,
                "price": None,
                "start_date": None,
                "end_date": None,
                "show_time": None,
                "running_time": None,
                "casting": None,
                "rating": None,
                "description": None,
                "poster_url": None,
                "open_date": None,
                "pre_open_date": None,
                "artist": None,
                "hosts": {"link": None, "site_id": 1}
            }

            # 공연 제목 추출
            title = soup.find('h2', class_='prdTitle')
            if title:
                ticket_data['title'] = title.text.strip()

            # 카테고리 (뮤지컬 등)
            category = soup.find('div', class_='tagText')
            if category:
                ticket_data['category'] = category.find_all('span')[0].text.strip()  # 첫 번째 span
            
            # 장소, 공연기간, 관람연령, 러닝타임 추출
            li_range = soup.find_all('li', class_='infoItem')
            for li in li_range:
                text = li.text
                if "장소" in text:
                    place = text.split("장소")[1].strip()
                    ticket_data['location'] = place.split(' (자세히)')[0].replace('\n', '').strip()
                elif "공연기간" in text:
                    date_range = text.split("공연기간")[1].strip()
                    if "~" in date_range:
                        start_date, end_date = date_range.split("~")
                        ticket_data["start_date"] = start_date.strip()
                        ticket_data["end_date"] = end_date.strip()
                    else:
                        ticket_data["start_date"] = ticket_data["end_date"] = date_range.strip()
                elif "관람연령" in text:
                    ticket_data["rating"] = text.split("관람연령")[1].strip()
                elif "공연시간" in text:
                    ticket_data["running_time"] = text.split("공연시간")[1].strip()
                    
            
            # 공연시간 추출
            content = soup.find('div',class_='contentDetail')
            show_time = content.text.replace('\n', '').strip()
            show_time = ' '.join(show_time.split())
            ticket_data['show_time']=show_time.strip()

            # 가격 추출 ####형식맞춰야함-현재 리스트안에 리스트 형태##################
            price_list = []
            price_elements = soup.find_all('li', class_='infoPriceItem')
            for price in price_elements:
                price_text = price.text.strip().split()
                if not any ("자세히" in item for item in price_text):
                    price_list.append(price_text)
            ticket_data["price"] = price_list
            ################### 리스트안에 딕셔너리형태로 만들때 #####################
                    #seat = price_text[0]  # 좌석 정보
                    #price_value = price_text[1].replace(",", "")  # 가격 정보에서 쉼표 제거
                    # 딕셔너리 형태로 저장
                    #price_list.append({"seat": seat, "price": price_value})
                    #ticket_data["price"] = price_list

            # 포스터 이미지 URL 추출
            poster_url = soup.find('img', class_='posterBoxImage')
            if poster_url:
                ticket_data["poster_url"] = poster_url['src']

            # 캐스팅 정보 추출
            role_list = []
            role_name = soup.find_all('div', class_='castingActor')
            for role in role_name:
                role = role.text.replace('\n','').strip()
                role_list.append({"role_name":role, "actor":None})
            actor_list = []
            actor_name = soup.find_all('div', class_='castingName')
            for actor in actor_name:
                actor = actor.text.replace('\n','').strip()
                actor_list.append(actor)
            for i, role in enumerate(role_list):
                if i < len(actor_list):
                    role["actor"] = actor_list[i]
            ticket_data['casting'] = role_list

            # 아티스트 정보 추출
            artist_data = []
            urls = soup.find_all('div', class_='castingProfile')
            for i, url in enumerate(urls):
                if i < len(actor_list):
                    img_tag = url.find('img', class_='castingImage')
                    if img_tag and 'src' in img_tag.attrs:
                        artist_url = img_tag['src']
                        artist_data.append({"artist_name": actor_list[i],
                                        "artist_url": artist_url
                                        })
            ticket_data['artist'] = artist_data
            

            # 수집한 데이터를 출력
            print(ticket_data)

            # 파일 처리 후 다음 파일로 넘어가기
            base_file_number += 1
        else:
            print("처리할 파일이 없습니다.")
            break  # 파일이 없으면 종료
# 함수 실행
html_parsing()
