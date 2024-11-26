from datetime import datetime
from datetime import timedelta
import os
from interpark.raw_open_page import extract_open_html
import selenium
from bs4 import BeautifulSoup

def test():
    get_data = extract_open_html()
    for data in get_data:
        if data is None:
            raise ValueError("extract_open_html()에서 None이 반환되었습니다.")
        hook = S3Hook(aws_conn_id='interpark')
        bucket_name = 't1-tu-data'
        print(data["num"])
        key = f'interpark/testtest.html'
        try:
            # 데이터를 문자열로 가정하고 io.StringIO로 처리
            soup = data["data"]  # 크롤링 데이터의 HTML 내용

            # BeautifulSoup 객체를 HTML 문자열로 변환
            if hasattr(soup, "prettify"):
                html_content = soup.prettify()  # 예쁘게 정리된 HTML

            if not html_content.strip():  # HTML 데이터가 비어 있는지 확인
                raise ValueError("HTML 데이터가 비어 있습니다.")

            file_obj = io.BytesIO(html_content.encode('utf-8'))

            # S3에 업로드
            hook.get_conn().put_object(
                Bucket=bucket_name,
                Key=key,
                Body=file_obj
            )
            print(html_content)
            
            print(f"S3에 업로드 완료: {bucket_name}/{key}")
        except Exception as e:
            print(f"S3 업로드 실패: {e}")
            raise

test()
