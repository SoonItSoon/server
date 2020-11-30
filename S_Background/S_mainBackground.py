import threading
import time
count = 0

def startTimer():
    # count 변수 사용 
    global count
    count += 1
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_default = f"{now_date} [S_mainBackground]"
    print(f"{log_default} {count} minutes ON..")
    timer = threading.Timer(60, startTimer)
    timer.start()


startTimer()
