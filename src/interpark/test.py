from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime
########################
import re


def html_parsing():
    aws_conn_id = 'interpark'  # Airflow 연결 ID
    bucket_name = 't1-tu-data'

    hook = S3Hook(aws_conn_id=aws_conn_id)

    base_file_number = 53550  # 시작 파일 번호
    end_file_number = base_file_number + 10 # 끝 파일 번호 설정

    # 파일 번호를 하나씩 증가시키면서 반복 처리
    #while True:###################################################테스트
    while base_file_number <= end_file_number:
        s3_key_prefix = f'interpark/{base_file_number}'
        files = hook.list_keys(bucket_name, prefix=s3_key_prefix)

        found_base_file_number_ = None
        for file in files:
            if file.startswith(f'interpark/{base_file_number}_'):
                found_base_file_number_ = file
                break

        # 첫 번째 파일 처리
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
                    base_file_number += 1
                    continue

            ticket_data = {
            "title": None,
            "duplicatekey": None,
            "category": None,
            "location": None,
            "region": None,
            "price": None,
            "start_date": None,
            "end_date": None,
            "running_time": None,
            "casting": None,
            "rating": None,
            "description": None,
            "poster_url": None,
            "open_date": None,
            "pre_open_date": None,
            "artist": None,
            "hosts": [{"site_id": 1, "ticket_url": None}]
            }

            # 가격 추출
            price_list = []
            price_elements = soup.find_all('li', class_='infoPriceItem')
            for price in price_elements:
                price_text = price.text.strip().split()
                #price_text = price.text.strip()
                if not any("자세히" in item for item in price_text):
                    print(price_text)

                 #좌석과 가격을 분리 (숫자와 원 단위 뒤에 공백이 올 경우)
                    if len(price_text) >= 2:
                        seat = price_text[:-1]
                        price = price_text[-1]
                        price_list.append({"seat": " ".join(seat), "price": price})
                    elif len(price_text) == 1:
                        price = None
                        seat = []
                        for i, item in enumerate(price_text):
                            if '원' in item:
                                # 가격을 '원'과 그 앞의 값까지 추출하여 price에 저장
                                price = f"{price_text[i-1]} {item}"
                                # 가격 앞의 좌석 정보
                                seat_info = " ".join(price_text[i-3:i-1])
                                # 가격과 좌석 정보를 딕셔너리로 추가
                                price_list.append({"seat": seat_info, "price": price})
            ticket_data["price"] = price_list
################################################################

            # 포스터 이미지 URL
            poster_url = soup.find('img', class_='posterBoxImage')
            if poster_url:
                ticket_data["poster_url"] = 'https:'+poster_url['src']
                if ticket_data["poster_url"] == None:
                    src_url = soup.find('img', class_="poster bgConcert")
                    if src_url and 'src' in src_url.attrs:
                        poster_url_src = src_url['src']
                        ticket_data['poster_url'] = 'https:'+poster_url_src
            
            print(ticket_data)

        base_file_number+=1



html_parsing()
                                           
