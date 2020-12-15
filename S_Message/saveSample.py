import pymysql
import csv

CSV_FILE = "DB_sample.csv"

amList = []
pdList = []
eqList = []

file = open(CSV_FILE, "r", encoding="utf-8")
reader = csv.reader(file)

for line in reader:
    amList.append(line[0], line[1], line[2], line[3], line[4], line[5])
    if line[5] == 1:
        print(line[0], line[2])
        pdList.append(line[0], line[6], line[7], line[8], line[9], line[10], line[11], line[12], line[13])
    elif line[5] == 2:
        print(line[0], line[2])
        eqList.append(line[0], line[7], line[14], line[15], line[16], line[17])

AlertMsgDB = pymysql.connect(
        user='kyeol',
        passwd='hee',
        host='127.0.0.1',
        db='AlertMsgDB',
        charset='utf8'
    )
# mid, send_date, msg, send_location, sender, disaster
insertSQL = "INSERT INTO AM VALUES (%s, %s, %s, %s, %s, %s)"
cursor = AlertMsgDB.cursor(pymysql.cursors.DictCursor)
cursor.executemany(insertSQL, amList)
AlertMsgDB.commit()
insertSQL = "INSERT INTO PD VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
cursor.executemany(insertSQL, pdList)
AlertMsgDB.commit()
insertSQL = "INSERT INTO EQ VALUES (%s, %s, %s, %s, %s, %s)"
cursor.executemany(insertSQL, eqList)
AlertMsgDB.commit()
cursor.close()
AlertMsgDB.close()