###################################
# Group        : S_Message
# Module       : S_getMsgData
# Purpose      : 국민재난안전포털에서 서버에 업데이트되지 않은 재난문자를 가져온다. 
#                발송된 재난문자가 있다면, S_labelMsgData를 호출한다. 
# Final Update : 2020-12-05
####################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

CSV_FILE = "/home/sslab-hpc/Cap2020/server/S_Message/AM_new_csv.csv"

train_data = pd.read_csv(CSV_FILE, names=["msg", "disaster"], encoding="utf-8")
train_data.message = train_data.message.astype(str)

train_a = train_data["message"]

tokenizer = Tokenizer()
tokenizer.fit_on_texts(intent_train)
sequences = tokenizer.texts_to_sequences(intent_train)
print(intent_train[1])

max_len = 30
intent_train = pad_sequences(sequences, maxlen = max_len)
print(intent_train[1])

model = load_model('mnist_mlp_model.h5')

predictions = model.predict(intent_train)

for pred in predictions:
   print(np.argmax(pred))

