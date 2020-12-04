###################################
# Group        : S_Message
# Module       : S_getMsgData
# Purpose      : 국민재난안전포털에서 서버에 업데이트되지 않은 재난문자를 가져온다. 
#                발송된 재난문자가 있다면, S_labelMsgData를 호출한다. 
# Final Update : 2020-12-04
####################################

from selenium import webdriver
import pymysql
import csv
from time import time, strftime, localtime, sleep
import re

# # DB 접속
# AlertMsgDB = pymysql.connect(
#     user='kyeol',
#     passwd='hee',
#     host='127.0.0.1',
#     db='AlertMsgDB',
#     charset='utf8'
# )
# # id, date, msg, send_platform, location_name, type
# insertSQL = "INSERT INTO alertMsg VALUES (%s, %s, %s, %s, %s, %s)"
# cursor = AlertMsgDB.cursor(pymysql.cursors.DictCursor)

CSV_FILE = "alertMsgData.csv"
# 가장 최근의 일련번호를 갖고있는 변수
lastMID = -1
# 실패한 일련번호를 저장하는 list
msgList = []
failList = []
# 국민재난안전포털 재난문자 URL
URL = "http://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgView.jsp?menuSeq=679"

# webdriver 설정
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('lang=ko_KR')

# csv 파일에서 
def getLastMID():
    global CSV_FILE
    file = open("CSV_FILE", "r", encoding="utf-8")
    reader = csv.reader(file)
    lastMID = -1
    for line in reader:
        lastMID = line[0]
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_default = f"{now_date} [S_getMsgData]"
    print(f"{log_default} getLastMID() : {lastMID}")
    return lastMID


def getSender(msg):
    search = re.search("\[(.+?)\]", msg)
    if search:
        sender = m.group(1).split(",")[0]
        sender = re.sub("[0-9\[\- ]", "", found)
    else:
        sender = ""
    return sender


def saveMsg2DB(msgList):
    # DB 접속
    AlertMsgDB = pymysql.connect(
        user='kyeol',
        passwd='hee',
        host='127.0.0.1',
        db='AlertMsgDB',
        charset='utf8'
    )
    # id, date, msg, send_platform, location_name, type
    insertSQL = "INSERT INTO AMtest VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = AlertMsgDB.cursor(pymysql.cursors.DictCursor)
    cursor.executemany(insertSQL, msgList)
    AlertMsgDB.commit()
    cursor.close()
    AlertMsgDB.close()


def saveMsg2CSV(msgList):
    # 재난문자 데이터 csv로 저장
    file = open("alertMsgData.csv", mode="a", newline="")
    writer = csv.writer(file)

    # writer.writerow(["일련번호", "발송시간", "내용", "발송주체", "발송지역", "재난구분"])
    for info in alertMsg:
        writer.writerow(info)

    file.close()


def getMsgData():
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_default = f"{now_date} [S_getMsgData]"
    global lastMID
    if lastMID = -1
        lastMID = getLastMID()
    index = lastMID
    # 브라우저 생성
    global chrome_options
    browser = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)
    browser.get(URL)
    # 재난문자를 임시 저장하는 list
    msgList = []
    received = True
    while received:
        nextBtn = browser.find_element_by_id("bbs_gubun")
        browser.execute_script("arguments[0].href = arguments[1]", nextBtn, f"javascript:articleDtl('63','{index}');")
        nextBtn.send_keys('\n')
        # 페이지가 로딩 중인 경우를 고려하여 정보가 표시되지 않을 경우 대기 후 재시도
        sendTime = browser.find_element_by_id("sj").text
        if len(sendTime) == 0:
            time.sleep(0.5)
        sendTime = browser.find_element_by_id("sj").text.split()

        failCnt = 0
        # 정보가 없는 경우 failList에 추가
        if len(sendTime) == 0:
            print(f"!!!{index}번 재난문자 실패({lastMID})!!!")
            failList.append(index)
            failCnt += 1
            if failCnt >= 3:
                tempList = failList[-3:]
                failList = [x for x in failList if x not in tempList]
                received = False
                continue
        # 정보가 있을 경우 추출 후 msgList에 저장
        else:
            failCnt = 0
            context = browser.find_element_by_id("cn").text.split("\n-송출지역-\n")
            # 전 지역으로 발송된 재난문자 (송출 지역 없음)
            if len(context) < 2:
                context.append("")
            # 재난문자 데이터 가공
            sendingDate = sendTime[0].replace('/', '-') + " " + sendTime[1]
            msg = context[0].replace("\n", " ")
            sender = getSender(msg)
            locationName = context[1].replace("\n", ",")
            disasterType = ""
            # 재난문자 데이터 임시 저장
            msgList.append([index, sendingDate, msg, sender, locationName, disasterType])
            print(f"[S_getMsgData] SUCCESS loading {{id: {index}, date: {sendingDate}, msg: {msg}, send_platform: {sender}, location_name: {locationName}, type: {disasterType}}}({len(alertMsg)})")
            lastMID = index + 1
            print(f"!!!{index}번 재난문자 성공!!!")
        index += 1
    browser.quit()

    # 추출한 재난문자가 있다면 AlertMsg.AM에 저장
    if len(msgList) > 0:
        saveMsg2DB(msgList)
        # saveMsg2CSV(msgList)
        print(f"!!!재난문자{len(msgList)}개 저장 완료({lastMID})!!!")
        msgList.clear()

