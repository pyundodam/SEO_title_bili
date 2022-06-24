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
from googletrans import Translator
import wordcloud
from wordcloud import WordCloud
import matplotlib.pyplot as plt

print("\n오늘 비리비리의 인기 키워드를 확인합니다.\n")

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

    # URL 세팅
    Url = 'https://www.bilibili.com/v/popular/rank/all'

    print("\n크롤링을 시작합니다!\n")

    # 리스트
    title_lst=[]

    # 크롤링
    for first in range(1):
        wait = WebDriverWait(driver, 20)
        driver.get(Url)
        time.sleep(3)

        # 제목
        try:
            for title in tqdm(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'title')))): 
                title_temp = title.text
                title_lst.append(title_temp) #리스트에 추가
        except:
            # 크롤링 값이 없을 경우에
            # title_lst.append('') #공백넣기
            xyz = 0

    del title_lst[0]

    # 형태소 추출

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
        # emtpy = re.sub(' ','',alpha) # 공백 제거
        null = alpha.replace('\n',' ') # 줄바꿈 제거
        return null

    # 형태소 분석 함수
    def get_words(text): 
        text = nlp(text)
        txt = [f'{text.text}' for text in text.sentences for text in text.words] 
        return txt

    # 불용어처리
    list_file = open('stopwords(HC).txt', 'r', encoding="utf-8").readlines()
    stopwords = [x.strip() for x in list_file]

    # 키워드 추출하기
    m = 0
    for title in title_lst:
        re_title = regex_txt(str(title_lst[m]))
        words = get_words(re_title)
        remove_stopword = [x for x in words if x not in stopwords]
        keyword_lst.append(remove_stopword)
        m += 1


    # print(keyword_lst)

    # break

    #데이터프레임화
    df = pd.DataFrame({'title':title_lst})
    df['rcmd_keyword'] = keyword_lst
    df.index = df.index+1 #인덱스 1부터 시작
    # print(tabulate(df.head(20)))

    # 영상의 키워드 카운트 정렬
    video_keyword = [] 
    for head in tqdm(keyword_lst):
        head = get_words(regex_txt(str(keyword_lst)))
        video_keyword.append(head)

    data_count = Counter(head)
    notone = Counter({x : data_count[x] for x in data_count if len (x) > 1})
    key_rank= notone.most_common(20) #상위 20개 키워드 담기
    key_rank_df = pd.DataFrame(key_rank, columns=['rcmd_keyword', 'count'])
    key_rank_df.index = key_rank_df.index+1 #인덱스 1부터 시작
    print("\n","주요 키워드를 추출을 완료했습니다",'\n')
    print(tabulate(key_rank_df))

    # 번역하기
    translator = Translator()

    # 키워드번역
    trans_lst = []
    r=0
    print("\n키워드 번역중...\n")
    for trans_key in tqdm(key_rank):
        trans_k_temp = regex_txt(str(key_rank[r]))
        try:
            trans_result = translator.translate(str(trans_k_temp),dest='ko').text
            trans_lst.append(trans_result)
        except:
            # 크롤링 값이 없을 경우에
            trans_lst.append('') #공백넣기
        r += 1

    key_rank_df['trans_rcmd_keyword'] = trans_lst
    modified_date = datetime.datetime.now().strftime("%Y-%m-%d")
    key_rank_df['modified_date'] = modified_date


    # 워드 클라우드 생성
    for_wordcloud = [n for n in head if len(n) > 1]
    noun_text = ''

    for word in for_wordcloud:
        noun_text = noun_text +' '+word

    wordcloud = WordCloud(font_path='msyhbd', max_font_size=60, relative_scaling=.5).generate(noun_text) # generate() 는 하나의 string value를 입력 받음
    plt.figure()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    # plt.show() # 워드클라우드 보기

    # 파일 저장 
    filename = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    key_rank_df.to_excel('추천 키워드 ' + filename + '.xlsx')

    # 웹 끄기
    driver.close()
    print("\ndone!\n")
    print(input("계속하시려면 아무키나 누르세요"))
    time.sleep(2)

