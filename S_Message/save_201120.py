import pymysql
import csv
from selenium import webdriver
import time

# DB 접속
AlertMsgDB = pymysql.connect(
    user='kyeol',
    passwd='hee',
    host='127.0.0.1',
    db='AlertMsgDB',
    charset='utf8'
)
# id, date, msg, send_platform, location_name, type
insertSQL = "INSERT INTO alertMsg VALUES (%s, %s, %s, %s, %s, %s)"
cursor = AlertMsgDB.cursor(pymysql.cursors.DictCursor)

# 국민재난안전포털 (2020-11-20 10:00까지)
URL = "http://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgView.jsp?menuSeq=679"
# 완료한 내역 : 1~65924
pageMin = 65925
pageMax = 65925
alertMsg = []
failed = []

# webdriver 실행
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('lang=ko_KR')
browser = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)
browser.get(URL)

# 국민재난안전포털 스크래핑
for index in range(pageMin, pageMax + 1):
# for index in [23623, 23625, 24410, 24518, 24913, 24999, 25076, 26266, 27294, 27299, 31993, 34430, 35057, 44665, 45733, 47479, 48758, 50010, 53035, 54124, 55945, 63851]:
    # 다음 페이지 로딩
    nextBtn = browser.find_element_by_id("bbs_gubun")
    browser.execute_script("arguments[0].href = arguments[1]", nextBtn, f"javascript:articleDtl('63','{index}');")
    nextBtn.send_keys('\n')

    # 페이지가 로딩 중인 경우를 고려하여 정보가 표시되지 않을 경우 대기
    sendTime = browser.find_element_by_id("sj").text
    if len(sendTime) == 0:
        time.sleep(0.5)
    
    # 정보가 없는 경우 넘어가고, 있을 경우 추출 후 저장
    sendTime = browser.find_element_by_id("sj").text.split()
    if len(sendTime) == 0:
        print(f"[S_getMsgData] FAILED loading page {index}({len(alertMsg)})")
        failed.append(index)
    else:
        context = browser.find_element_by_id("cn").text.split("\n-송출지역-\n")
        if len(context) < 2:
            context.append("")
        # 재난문자 데이터 가공
        sendingDate = sendTime[0].replace('/', '-') + " " + sendTime[1]
        msg = context[0].replace("\n", "")
        if msg.startswith("["):
            sender = msg.split("[")[1].split("]")[0].split(",")[0].split(" ")[0]
        else:
            sender = ""
        locationName = context[1].replace("\n", ",")
        disasterType = ""

        # 재난문자 데이터 임시 저장
        alertMsg.append([index, sendingDate, msg, sender, locationName, disasterType])
        print(f"[S_getMsgData] SUCCESS loading {{id: {index}, date: {sendingDate}, msg: {msg}, send_platform: {sender}, location_name: {locationName}, type: {disasterType}}}({len(alertMsg)})")
browser.quit()
print(f"[S_getMsgData] {len(alertMsg)}개 재난문자 추출 완료!")
print(f"[S_getMsgData] {len(failed)}개 재난문자 추출 실패 {failed}")

# 재난문자 데이터 AlertMsgDB.alertMsg에 저장
cursor.executemany(insertSQL, alertMsg)
AlertMsgDB.commit()
print(f"[S_getMsgData] 재난문자 AlertMsgDB.alertMsg에 저장 완료!")

# 재난문자 데이터 csv로 저장
file = open("alertMsgData.csv", mode="a", newline="")
writer = csv.writer(file)

# writer.writerow(["일련번호", "발송시간", "내용", "발송주체", "발송지역", "재난구분"])
for info in alertMsg:
    writer.writerow(info)

file.close()

print(f"[S_getMsgData] 재난문자 alertMsgData.csv에 저장 완료!")
