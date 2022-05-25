import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm.auto import tqdm
import re
import stanza
from collections import Counter
from tabulate import tabulate

while True:
 print("\n 기다리세요...")
# 크롤링 전 세팅
 chrome_options = Options()
 chrome_options.add_experimental_option("detach", True)

 chrome_options.add_argument("disable-gpu")
 chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36")
 chrome_options.add_argument('headless')

 service = Service(executable_path=ChromeDriverManager().install())
 driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
# driver.maximize_window()


# 크롤링
 baseURL = 'https://search.bilibili.com/video?keyword='
 keyword = input("\n 검색어를 입력하세요 >>> ")
 Url = baseURL + keyword

 print("\n☞   "+keyword+"  ☜"+"   (으)로 크롤링을 시작합니다!\n")

# 리스트
 title_lst=[]
 link_lst =[]
 view_count_lst =[]
 like_count_lst = []
 date_lst = []

 wait = WebDriverWait(driver, 20)
 driver.get(Url) # 영상 url
 time.sleep(3)

# 제목
 try:
     for title in tqdm(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'bili-video-card__info--tit')))): 
         title_temp = title.text
         title_lst.append(title_temp) #리스트에 추가
 except:
    # 크롤링 값이 없을 경우에
     title_lst.append('') #공백넣기

# 조회수, 좋아요수
 playLike_count_lst =[]
 try:
     for playLike in tqdm(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'bili-video-card__stats--item')))): 
         like_temp = playLike.text
         playLike_count_lst.append(like_temp)
 except:
    # 크롤링 값이 없을 경우에
     playLike_count_lst.append('') #공백넣기

 view_count = playLike_count_lst[0::2] #홀수 리스트로 나누기
 like_count = playLike_count_lst[1::2] #짝수 리스트로 나누기

# 업로드일
 raw_date_lst = []
 try:
     for date in tqdm(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'bili-video-card__info--date')))): 
         date_temp = date.text
         raw_date_lst.append(date_temp) #리스트에 추가
 except:
    # 크롤링 값이 없을 경우에
     raw_date_lst.append('') #공백넣기
 n=0
 for i in raw_date_lst:
     date = re.sub(". ", "", str(raw_date_lst[n])) #. 제거
     date_lst.append(date)
     n += 1

 print("크롤링 완료!\n")
 time.sleep(2)
 print("키워드 추출을 시작합니다!\n")

# 키워드 추출 (상위 5개)
 keyword_lst = []

 stanza.download('zh',processors='tokenize,pos')
 nlp = stanza.Pipeline('zh', processors='tokenize,pos')

# 숫자 단위 변환 함수
 def unit_change(list):
     for list in list:
         dot = re.sub('[.]',"",str(list)) # . 제거
         unit =  re.sub('[万]',"0000",dot) # 万,亿 제거
     return unit

# 텍스트 전처리 함수
 def regex_txt(text): 
     parse = re.sub(r'[^\w\s]','',text) # 특수문자 제거
     num = re.sub(r'\d+',' ',parse) # 숫자 제거
     # eng = re.sub('[a-zA-Z]' , ' ', num) # 영어 제거
     alpha = num.lower() #소문자로 바꾸기
     emtpy = re.sub(' ','',alpha) # 공백 제거
     null = emtpy.replace('\n',' ') # 줄바꿈 제거
     return null

# 형태소 분석 함수
 def get_words(text): 
     text = nlp(text)
     txt = [f'{text.text}' for text in text.sentences for text in text.words] 
     return txt

# 키워드 추출하기
 m = 0
 for title in title_lst:
     re_title = regex_txt(str(title_lst[m]))
     words = get_words(re_title)
     keyword_lst.append(words)
     m += 1

#데이터프레임화
 df = pd.DataFrame({'제목':title_lst, '조회수':view_count, '좋아요수':like_count, '업로드일':date_lst})
 df['키워드'] = keyword_lst
 df.index = df.index+1 #인덱스 1부터 시작
 print("\n","상위 20개 영상의 키워드를 추출을 완료했습니다.", '\n')
 print(tabulate(df.head(20)))
# df.to_excel('데이터프레임.xlsx')

# 상위 10개 영상의 키워드 카운트 정렬
 ten_video_keyword = [] #상위 10개 키워드 카운트
 for head_Ten in keyword_lst:
     head_Ten = get_words(regex_txt(str(keyword_lst[:20])))
     ten_video_keyword.append(head_Ten)

 data_count = Counter(head_Ten)
 notone = Counter({x : data_count[x] for x in data_count if len (x) > 1})
 Key_rank= notone.most_common(5) #상위 5개 키워드 담기
 Key_rank_df = pd.DataFrame(Key_rank, columns=['키워드', '카운트'])
 print("\n","상위 20개 영상의 주요 키워드를 추출을 완료했습니다",'\n')
 print(tabulate(Key_rank_df))

 driver.close()
 print("\ndone!\n")
 print(input("계속하시려면 아무키나 누르세요"))
 time.sleep(2)

# 최고 조회수



# 최저 조회수
