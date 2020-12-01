from selenium import webdriver
import pymysql
import csv
from time import time, strftime, localtime, sleep

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
lastMID = -1
failList = []
URL = "http://www.safekorea.go.kr/idsiSFK/neo/sfk/cs/sfc/dis/disasterMsgView.jsp?menuSeq=679"


def getLastMID():
    file = open("alertMsgData.csv", "r", encoding="utf-8")
    reader = csv.reader(file)
    lastMID = -1
    for line in reader:
        lastMID = line[0]
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_default = f"{now_date} [S_getMsgData]"
    print(f"{log_default} getLastMID() : {lastMID}")
    return lastMID

def getMsgData():
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_default = f"{now_date} [S_getMsgData]"
    if lastMID = -1
        lastMID = getLastMID()


print(getLastMID())
