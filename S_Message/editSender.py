# CSV 파일의 sender를 재저장하는 프로그램

import csv
import re
from operator import itemgetter

CSV_FILE = "AM_csv.csv"
SAVE_FILE = "AM_csv_new.csv"

def getSender(msg):
    search = re.search("\[(.+?)\]", msg)
    if search:
        sender = search.group(1).split(",")[0].split()[0]
        sender = re.sub("[0-9①-⑮\[\- ]", "", sender)
        temp = sender.split("(")
        if len(temp[0]) > 0:
            sender = temp[0]
        elif len(temp) > 1:
            sender = temp[1]
        else:
            sender = ""
    else:
        sender = ""
    return sender

def saveMsg2CSV(msgList):
    # 재난문자 데이터 csv로 저장
    global SAVE_FILE
    file = open(SAVE_FILE, mode="a", newline="", encoding="utf-8")
    writer = csv.writer(file)

    for info in msgList:
        writer.writerow(info)

    file.close()

file_ori = open(CSV_FILE, mode="r", encoding="utf-8")
reader = csv.reader(file_ori)
msgList = []
senderDict = {}
# 2 -> 4
for line in reader:
    msg = line
    msg[4] = getSender(line[2])
    if msg[4] in senderDict.keys():
        senderDict[msg[4]] += 1
    else:
        senderDict[msg[4]] = 1
    msgList.append(msg)

# sorted(msgList, key=lambda msgList: msgList[0], reverse=False)
msgList.sort(key=itemgetter(0))
# res = sorted(senderDict.items(), key=lambda senderDict: senderDict[1], reverse=True)

# for count in range(0, len(res)):
#     print(res[count])
# print(len(res))
# for msg in msgList:
#     print(msg[0])

saveMsg2CSV(msgList)
