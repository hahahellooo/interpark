from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dateutil import parser

def convert_to_datetime_format(date_str):
    # 예시: "2024년 11월 6일(수) 오후 2시"
    # 오후/오전을 처리하기 위한 정규식
    am_pm = 'AM' if '오전' in date_str else 'PM'

    # 월, 일, 시간, 분 추출
    date_str = re.sub(r'[^\d\s가-힣]', '', date_str)  # 숫자와 공백 외 문자 제거
    date_match = re.search(r'(\d{1,2})월 (\d{1,2})일.*?(\d{1,2})시', date_str)

    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        hour = int(date_match.group(3))

        # 오전/오후를 반영해 시간 조정 (12시간제 → 24시간제)
        if am_pm == 'PM' and hour != 12:
            hour += 12
        elif am_pm == 'AM' and hour == 12:
            hour = 0

        # 날짜 형식에 맞춰 변환
        current_year = datetime.now().year  # 현재 년도 추출
        formatted_date = f"{current_year:04d}.{month:02d}.{day:02d} {hour:02d}:00"
        return formatted_date
    return None

def html_parsing():
    aws_conn_id = 'interpark'  # Airflow 연결 ID
    bucket_name = 't1-tu-data'

    hook = S3Hook(aws_conn_id=aws_conn_id)

    base_file_number = 53327  # 시작 파일 번호
    end_file_number = base_file_number + 5  # 끝 파일 번호 설정
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
            ticket_data = extract_data(soup)

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

                # 티켓오픈일, 선예매 추출
                ticket_open_date = None
                fanclub_preopen_date = None
                li_elements = base_soup.find_all('li')
                for li in li_elements:
                    strong_tag = li.find('strong')  # strong 태그 찾기
                    if strong_tag:
                        strong_text = strong_tag.text.strip()
                        if "티켓오픈일" in strong_text:
                            # 텍스트에서 날짜 추출
                            ticket_open_date = li.text.replace(strong_text, '').strip()
                            ticket_open_date = convert_to_datetime_format(ticket_open_date) ##
                        elif "선예매" in strong_text:
                            # 텍스트에서 날짜 추출
                            fanclub_preopen_date = li.text.replace(strong_text, '').strip()
                            fanclub_preopen_date = convert_to_datetime_format(fanclub_preopen_date)##
                if ticket_open_date:
                    ticket_data['open_date'] = ticket_open_date
                if fanclub_preopen_date:
                    ticket_data['pre_open_date'] = fanclub_preopen_date

                # 링크 추출
                book_link = base_soup.find('a', class_='btn_book')
                if book_link and 'href' in book_link.attrs:
                    ticket_data['hosts']['ticket_url'] = book_link['href']
            
                # 설명 추출
                desc = base_soup.find('div', class_='info1')
                description = desc.find('div', class_='data')
                if description:
                    description = description.text.strip()
                    ticket_data['description'] = description
                
                
            except Exception as e:
                print(f"Error while processing base file {base_file_number}: {e}")
        
        print(ticket_data)
        return ticket_data
    base_file_number+=1
    


def extract_data(soup):
    """BeautifulSoup 객체에서 데이터를 추출하는 함수"""
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

    # 공연 제목
    title = soup.find('h2', class_='prdTitle')
    if title:
        ticket_data['title'] = re.sub(r'\s+|[^\w가-힣0-9]', '', title.text)

    # 카테고리
    category = soup.find('div', class_='tagText')
    if category:
        ticket_data['category'] = category.find_all('span')[0].text.strip()

    # 장소, 공연기간, 관람연령, 러닝타임
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

    # 공연시간
    #content = soup.find('div', class_='contentDetail')
    #if content:
    #    show_time = content.text.replace('\n', '').strip()
    #    show_time = ' '.join(show_time.split())
    #    ticket_data['show_time'] = show_time

    # 가격
    price_list = []
    price_elements = soup.find_all('li', class_='infoPriceItem')
    for price in price_elements:
        price_text = price.text.strip().split()
        if not any("자세히" in item for item in price_text):
            if len(price_text) >= 2:
                seat = price_text[0]
                price = price_text[1]
                price_list.append({"seat": seat, "price": price})
    ticket_data["price"] = price_list

    # 포스터 이미지 URL
    poster_url = soup.find('img', class_='posterBoxImage')
    if poster_url:
        ticket_data["poster_url"] = 'https:'+poster_url['src']

    # 캐스팅 정보
    role_list = []
    role_name = soup.find_all('div', class_='castingActor')
    for role in role_name:
        role = role.text.replace('\n', '').strip()
        role_list.append({"role": role, "actor": None})
    actor_list = []
    actor_name = soup.find_all('div', class_='castingName')
    for actor in actor_name:
        actor = actor.text.replace('\n', '').strip()
        actor_list.append(actor)
    for i, role in enumerate(role_list):
        if i < len(actor_list):
            role["actor"] = actor_list[i]
    ticket_data['casting'] = role_list

    # 아티스트 정보
    artist_data = []
    urls = soup.find_all('div', class_='castingProfile')
    for i, url in enumerate(urls):
        if i < len(actor_list):
            img_tag = url.find('img', class_='castingImage')
            if img_tag and 'src' in img_tag.attrs:
                artist_url = 'https:'+img_tag['src']
                artist_data.append({"artist_name": actor_list[i],
                                    "artist_url": artist_url})
    ticket_data['artist'] = artist_data

    return ticket_data

# 함수 실행
html_parsing()

