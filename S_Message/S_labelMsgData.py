###################################
# Group        : S_Message
# Module       : S_labelMsgData
# Purpose      : 순환신경망으로 학습된 분류 모델을 이용하여, 
#                입력받은 재난문자를 분석 후 데이터베이스에 추가한다. 
# Final Update : 2020-12-11
####################################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import csv, time

NEW_FILE = "/home/sslab-hpc/Cap2020/server/S_Message/newMsg.csv"
model = load_model("/home/sslab-hpc/Cap2020/server/S_Message/mnist_mlp_model.h5")

def saveTempCSV(msgList):
    global NEW_FILE
    file = open(NEW_FILE, mode="w", newline="")
    file.truncate()

    writer = csv.writer(file)

    writer.writerow(["msg"])
    for msg in msgList:
        writer.writerow([msg[2]])
    file.close()


def labelDisaster(msgList):
    global NEW_FILE
    train_data = pd.read_csv(NEW_FILE, names=["msg"], encoding="utf-8")
    train_data.msg = train_data.msg.astype(str)
    train_a = train_data["msg"]
    intent_train = train_a.values.tolist()
    # print(intent_train[16761])
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(intent_train)
    sequences = tokenizer.texts_to_sequences(intent_train)
    max_len = 30
    intent_train = pad_sequences(sequences, maxlen = max_len)
    # print(intent_train[16761])
    global model
    model = load_model("/home/sslab-hpc/Cap2020/server/S_Message/mnist_mlp_model.h5")
    predictions = model.predict(intent_train)
    disasterDict = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
    
    disasterList = []
    i = 0
    first = 1
    for pred in predictions:
        if first:
            first = 0
            continue
        disasterDict[np.argmax(pred)] += 1
        # print(f"{msgList[i][2]} : {np.argmax(pred)}")
        i += 1
        disasterList.append(np.argmax(pred))
    print(disasterDict)

    return disasterList


def labelMsgData(msgList):
    start_time = time.time()
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
    log_default = f"{now_date} [S_labelMsgData]"
    print(f"{log_default} Start S_labelMsgData")
    saveTempCSV(msgList)
    disasterList = labelDisaster(msgList)
    end_time = time.time()
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
    print(f"{log_default} End S_labelMsgData (Process Time : {(end_time-start_time):.3f}s)")


