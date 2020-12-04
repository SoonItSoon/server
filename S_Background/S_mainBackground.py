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
    print(f"{log_default} {count} minutes ON..")
    getMsgData()
    timer = threading.Timer(60, startTimer)
    timer.start()


startTimer()
