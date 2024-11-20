from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_open_page_url(base_num, max_pages):
    # 브라우저 옵션 설정
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1900, 1000)

    # 결과 데이터 저장
    open_page_list = []

    # base_num부터 시작해 max_pages 만큼 반복
    for num in range(base_num, base_num + max_pages):
        try:
            open_page_url = f'https://ticket.interpark.com/webzine/paper/TPNoticeView.asp?bbsno=34&pageno=233&stext=&no={num}&groupno={num}&seq=0&KindOfGoods=TICKET&Genre=&sort=WriteDate'
            driver.get(open_page_url)
            open_page_list.append(open_page_url)

        except:
            print("open_page_url 접속 에러")
    print(open_page_list)        
    return open_page_list


           

