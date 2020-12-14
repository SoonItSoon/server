import threading
import time
import sys
sys.path.append("../S_Message")
from S_Message.S_getMsgData import getMsgData
count = 0

def startTimer():
    # count 변수 사용 
    global count
    count += 1
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_default = f"{now_date} [S_mainBackground]"
    start_time = time.time()
    print(f"{log_default} S_getMsgData start : {now_date}")
    getMsgData()
    end_time = time.time()
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_default = f"{now_date} [S_mainBackground]"
    print(f"{log_default} End S_labelMsgData (Total Process Time : {(end_time-start_time):.3f}s)")
    timer = threading.Timer(60, startTimer)
    timer.start()


startTimer()
