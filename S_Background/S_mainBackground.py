import threading

count = 0

def startTimer():
    # count 변수 사용 
    global count
    count += 1
    print(f"[S_mainBackground] {count} minutes ON..")
    timer = threading.Timer(60, startTimer)
    timer.start()


startTimer()
