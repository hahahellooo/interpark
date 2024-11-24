import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def get_open_page_url(base_num, max_pages):
    
    # ChromePtions 객체 생성
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")

    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 결과 데이터 저장
    open_page_list = []
   

    # base_num부터 시작해 max_pages 만큼 반복
    for num in range(base_num, base_num + max_pages):
        try:
            open_page_url = f'https://ticket.interpark.com/webzine/paper/TPNoticeView.asp?bbsno=34&pageno=233&stext=&no={num}&groupno={num}&seq=0&KindOfGoods=TICKET&Genre=&sort=WriteDate'
            driver.get(open_page_url)
            print(open_page_url)
            status_code = driver.execute_script(
                "return (window.performance.getEntries()[0] || {}).responseStart ? 200 : 404;"
            )
            if status_code == 200:
                open_page_list.append(open_page_url)    
            else:
                print("오류 페이지 발견. 데이터를 추가하지 않습니다.")
               

        except:
            print("open_page_url 접속 에러")
    print(open_page_list)        
    return open_page_list



           

