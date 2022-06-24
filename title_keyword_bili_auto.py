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
import os

# 추천키워드 엑셀파일 읽어오기
def getFileList():
    path = os.path.abspath(".")
    print(path)
    for root, dirs, files in os.walk(path):
        return files
    return []


print("\n영상 주제 및 제목 추천 키워드를 확인합니다...\n")

def crawling(firstURL,title_lst,date_lst,play_lst):

    
    wait = WebDriverWait(driver, 20)
    driver.get(firstURL)
    time.sleep(3)

    # 제목
    try:
        for title in tqdm(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'bili-video-card__info--tit')))): 
            title_temp = title.text
            if title_temp == '':
                pass
            else :
                title_lst.append(title_temp) #리스트에 추가
    except:
        # 크롤링 값이 없을 경우에
        # title_lst.append('') #공백넣기
        # xyz = 0
        pass

    # 업로드일
    raw_date_lst = []
    try:
        for date in tqdm(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'bili-video-card__info--date')))): 
            date_temp = date.text
            if date_temp == '':
                pass
            else :
                raw_date_lst.append(date_temp) #리스트에 추가
    except:
        # 크롤링 값이 없을 경우에
        # raw_date_lst.append('') #공백넣기
        pass
    n=0
    for i in raw_date_lst:
        date = re.sub(". ", "", str(raw_date_lst[n])) #. 제거
        date_lst.append(change_date(date))
        n += 1

    # 조회수
    try:
        for play in tqdm(wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'bili-video-card__mask > div > div > span:nth-child(1)')))): 
            play_temp = play.text
            if play_temp == '':
                pass
            else :
                play_lst.append(change_wan(play_temp)) #리스트에 추가
    except:
        # 크롤링 값이 없을 경우에
        # title_lst.append('') #공백넣기
        pass

    return
def change_date(x):

        now = datetime.datetime.now()
        day_before_1 = now - datetime.timedelta(days=1)
        this_year_pattern = r'\d-\d'

        if "小时前" in x:
                return x.replace(x,now.strftime("%d-%m-%Y"))
        elif '分钟前' in x :
                return x.replace(x,now.strftime("%d-%m-%Y"))
        elif '昨天'in x :
                return x.replace(x,day_before_1.strftime("%d-%m-%Y"))
        elif re.match(this_year_pattern,x):
            return "2022-"+ x
        else : 
                return x
def regex_txt(text): 
    parse = re.sub(r'[^\w\s]','',text) # 특수문자 제거
    num = re.sub(r'\d+',' ',parse) # 숫자 제거
    # eng = re.sub('[a-zA-Z]' , ' ', num) # 영어 제거
    alpha = num.lower() #소문자로 바꾸기
    emtpy = re.sub(' ','',alpha) # 공백 제거
    null = emtpy.replace('\n',' ') # 줄바꿈 제거
    return null
def get_words(text): 
    text = nlp(text)
    txt = [f'{text.text}' for text in text.sentences for text in text.words] 
    return txt
def change_wan(y):
    if y.endswith('万'):
        return int(eval(y[:-1]) * 10000)
    else:
        return y


# 세팅
if (1==1):

    files = getFileList()
    for fname in files:
        if fname.find("추천")>=0:
            break
    
    # 키워드 파일 읽어오기
    file = pd.read_excel(fname)
    keyword_path = file['rcmd_keyword']

    # URL 세팅
    baseURL = 'https://search.bilibili.com/video?keyword='
    pagenext = 3
    addURL = "&page="

    # 새로운 엑셀 파일 생성
    filename = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    writer = pd.ExcelWriter("제목키워드" + ' ('+str(pagenext)+'P) '+filename+ ' .xlsx' , engine='xlsxwriter')

    print("\n 기다리세요...\n")

    # 형태소 분석기 세팅
    stanza.download('zh',processors='tokenize,pos')
    nlp = stanza.Pipeline('zh', processors='tokenize,pos')

    # 크롤링 전 세팅
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36")
    #  chrome_options.add_argument('headless')

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
    # driver.maximize_window()

# 분석시작
j=1
for auto in tqdm(keyword_path):

    print("\n☞   "+ auto +"  ☜"+"   (으)로 크롤링을 시작합니다!\n")

    # 리스트
    title_lst=[]
    date_lst = []
    play_lst = []


    for index in range(1,int(pagenext)+1):
        # twoURL = baseURL + keyword + addURL + str(pageNum)
        twoURL = baseURL + auto + addURL + str(index)
        crawling(twoURL,title_lst,date_lst,play_lst)

    # 형태소 추출


    print("크롤링 완료!\n")
    time.sleep(2)
    print("키워드 추출을 시작합니다!\n")

    # 불용어처리
    list_file = open('stopwords(HC).txt', 'r', encoding="utf-8").readlines()
    stopwords = [x.strip() for x in list_file]

    # 키워드 추출하기
    keyword_lst = []
    m = 0
    for title in title_lst:
        re_title = regex_txt(str(title_lst[m]))
        words = get_words(re_title)
        remove_stopword = [x for x in words if x not in stopwords]
        keyword_lst.append(remove_stopword)
        m += 1


    #데이터프레임화
    modified_date = datetime.datetime.now().strftime("%Y-%m-%d")
    df = pd.DataFrame({'title':title_lst, 'upload_date':date_lst, 'play_count':play_lst})
    df['upload_date'] = pd.to_datetime(df['upload_date'],infer_datetime_format=True)
    df['modified_date'] = modified_date
    df['title_keyword'] = keyword_lst
    df['rcmd_keyword'] = auto
    df.index = df.index+1 #인덱스 1부터 시작
    print(tabulate(df.head(20)))
    

    # 키워드 추출
    video_keyword = [] 
    for head in tqdm(keyword_lst):
        head = get_words(regex_txt(str(keyword_lst)))
        video_keyword.append(head)

    # 영상의 키워드 카운트 정렬
    data_count = Counter(head)
    notone = Counter({x : data_count[x] for x in data_count if len (x) > 1})
    key_rank= notone.most_common(20) #상위 20개 키워드 담기
    key_rank_df = pd.DataFrame(key_rank, columns=['title_keyword', 'count'])
    key_rank_df['modified_date'] = modified_date
    key_rank_df.index = key_rank_df.index+1 #인덱스 1부터 시작
    print("\n","주요 키워드를 추출을 완료했습니다",'\n')
    print(tabulate(key_rank_df))
    

    # 번역하기
    translator = Translator()

    # 키워드번역
    trans_k_lst = []
    r=0
    print("\n키워드 번역중...\n")
    for trans_key in tqdm(key_rank):
        trans_k_temp = regex_txt(str(key_rank[r]))
        try:
            trans_k_result = translator.translate(str(trans_k_temp),dest='ko').text
            trans_k_lst.append(trans_k_result)
        except:
            # 크롤링 값이 없을 경우에
            trans_k_lst.append('') #공백넣기
        r += 1

    key_rank_df['trans_keyword'] = trans_k_lst

    # 제목번역
    trans_t_lst = []
    p =0
    print("\n제목 번역중...\n")
    for tran_title in tqdm(title_lst):
        trans_t_temp = regex_txt(str(title_lst[p]))
        try:
            trans_t_result = translator.translate(str(trans_t_temp),dest='ko').text
            trans_t_lst.append(trans_t_result)
        except:
            # 크롤링 값이 없을 경우에
            trans_t_lst.append('') #공백넣기
        p += 1

    df['trans_title'] = trans_t_lst

    print("번역: ", pd.DataFrame(trans_k_lst))

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
    # plt.savefig(auto+str(pagenext)+'wordcloud.png')

    # 데이터프레임 엑셀 저장
    df.to_excel(writer, sheet_name='sheet'+str(j)+ "("+auto+")")
    key_rank_df.to_excel(writer, sheet_name='★sheet'+str(j)+"-1" "("+auto+")")
    # pd.DataFrame(trans_k_lst).to_excel(writer, sheet_name='sheet3')
    # pd.DataFrame(trans_t_lst).to_excel(writer, sheet_name='sheet3')
    
    # 웹 끄기
    # driver.close()
    print(str(j)+"번째 완료!\n")
    # print(input("계속하시려면 아무키나 누르세요"))
    time.sleep(2)
    j += 1

# 엑셀 파일 저장
writer.save()