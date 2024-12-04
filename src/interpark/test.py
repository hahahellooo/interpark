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

    base_file_number = 52535  # 시작 파일 번호
    end_file_number = base_file_number + 3  # 끝 파일 번호 설정

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

                # 예매하기 페이지에서 1차 데이터 추출
                #ticket_data = extract_data(soup)
                ticket_data = {
                    "title": None,
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
                    "hosts": {"site_id": 1, "ticket_url": None}
                        }

                # None 값이 남아있는 경우 base_file_number로 다시 추출
                if any(value is None for key, value in ticket_data.items() if key != "hosts"):
                    print("Some values are None. Checking base file.")
                    try:
                        base_file_html = hook.read_key(f'interpark/{base_file_number}.html', bucket_name)
                        base_soup = BeautifulSoup(base_file_html, 'html.parser')

                        # 제목 추출
                        info_title = base_soup.find('div', class_='info')
                        title = info_title.find('h3')
                        title = title.text.strip()
                        if title:
                            if ticket_data['title'] is None:
                                ticket_data['title'] = re.sub(r'\s+|[^\w가-힣0-9]', '', title)

                        # 공연기간 추출
                        introduce = base_soup.find('div', class_='introduce')
                        data = introduce.find('div', class_='data')
                        if data and ticket_data['start_date'] == None:
                            p = data.find('p').text.strip()
                            lines = p.strip().split('\n')
                            for line in lines:
                                line = line.replace(" ","").strip()
                                if "공연일시" in line or "일시" in line or "공연기간" in line or "공연일자" in line:
                                    date = line.split(":")[1].split("~")  # ':' 이후를 가져오고 '~' 기준으로 분리
                                    if len(data) ==1:
                                        start_date_raw = date[0].strip()
                                        end_date_raw = start_date_raw
                                    else:
                                        start_date_raw = date[0].strip()
                                        end_date_raw = date[1].strip()
                                    # 시작 날짜 처리 (2024년 12월 14일(토) -> 2024.12.14)
                                    start_date_match = re.search(r'(\d{4})년(\d{1,2})월(\d{1,2})일', start_date_raw)
                                    if start_date_match:
                                        start_date = f"{start_date_match.group(1)}.{int(start_date_match.group(2)):02d}.{int(start_date_match.group(3)):02d}"
                                        # 종료 날짜 처리 (12월 15일(일) -> 2024.12.15)
                                        end_date_match = re.search(r'(\d{1,2})월(\d{1,2})일', end_date_raw)
                                        if end_date_match:
                                            # start_date에서 년도 추출
                                            year_from_start = start_date_match.group(1)
                                            # end_date에 년도 추가
                                            end_date = f"{year_from_start}.{int(end_date_match.group(1)):02d}.{int(end_date_match.group(2)):02d}"
                                        ticket_data['start_date'] = start_date
                                        ticket_data['end_date'] = end_date

                        # 설명 추출
                        desc = base_soup.find('div', class_='info1')
                        description = desc.find('div', class_='data')
                        if description:
                            description = description.text
                            description = ' '.join(description.split())
                            ticket_data['description'] = description
                        
                        ############################################################ 가격 추출
                        price_list = []
                        price_elements = soup.find_all('li', class_='infoPriceItem')
                        for price in price_elements:
                            print(price)
                            price_text = price.text.strip().split("석")
                            print(price_text)
                            if not any("자세히" in item for item in price_text):
                                if len(price_text) >= 2:
                                    seat = price_text[0]
                                    price = price_text[-1]
                                    price_list.append({"seat": seat, "price": price})
                        ticket_data["price"] = price_list
                    except Exception as e:
                        print(f"Error while processing base file {base_file_number}: {e}")

            print(ticket_data)
        else:
            print("처리할 파일이 없습니다.")
        base_file_number+=1
        continue


html_parsing()
                                           
