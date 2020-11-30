from selenium import webdriver
import pymysql
import csv
from time import sleep

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

def getLastMID():
    file = open("alertMsgData.csv", "r", encoding="utf-8")
    reader = csv.reader(file)
    print(reader[-1])

getLastMID()