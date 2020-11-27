from flask import Flask, render_template, request
import json

app = Flask("Hello World!")

levelDict = {1: {1: "접촉안내", 2: "동선공개", 3: "발생안내", 9: "캠페인"},
                2: {1: "지진", 9: "기타"},
                3: {1: "경보", 2: "주의보", 9: "저감조치"},
                4: {1: "경보", 2: "주의보", 9: "조치조치"},
                5: {1: "경보", 2: "주의보", 9: "조치알림"},
                6: {1: "경보", 2: "주의보", 9: "기타"},
                7: {1: "경보", 2: "주의보", 9: "기타"},
                8: {1: "경보", 2: "주의보", 9: "기타"},
                9: {1: "경보", 2: "주의보", 9: "기타"}}

@app.route("/")
def home():
    print("[S_sendServerData] REST request : '/'")
    return render_template("home.html")

@app.route("/search")
def search():
    # 공통
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    main_location = request.args.get("main_location")
    sub_location = request.args.get("sub_location")
    disaster = int(request.args.get("disaster"))
    req_levels = request.args.get("level").split(",")
    inner_text = request.args.get("inner_text")

    levels = []
    for req_level in req_levels:
        levels.append(levelDict[disaster][int(req_level)])
    log = ""
    # 전염병
    if disaster == 1:
        name = request.args.get("name")
        if inner_text:
            log = {"재난": f"전염병 {name} {levels}", "날짜": f"{start_date} ~ {end_date}", "위치": f"{main_location} {sub_location}", "텍스트 검색": "{inner_text}"}
        else:
            log = {"재난": f"전염병 {name} {levels}", "날짜": f"{start_date} ~ {end_date}", "위치": f"{main_location} {sub_location}"}
    # 지진
    elif disaster == 2:
        scale_min = float(request.args.get("scale_min"))
        scale_max = float(request.args.get("scale_max"))
        obs_location = request.args.get("obs_location")
        if inner_text:
            if obs_location:
                log = {"재난": f"지진 {levels}", "날짜": f"{start_date} ~ {end_date}", "위치": f"{main_location} {sub_location}(으)로 전송된 {obs_location}에서 발생한 지진", "진도":f"{scale_min} ~ {scale_max}", "텍스트 검색": f"{inner_text}"}
            else:
                log = {"재난": f"지진 {levels}", "날짜": f"{start_date} ~ {end_date}", "위치": f"{main_location} {sub_location}(으)로 전송된 전국에서 발생한 지진", "진도":f"{scale_min} ~ {scale_max}", "텍스트 검색": f"{inner_text}"}
        else:
            if obs_location:
                log = {"재난": f"지진 {levels}", "날짜": f"{start_date} ~ {end_date}", "위치": f"{main_location} {sub_location}(으)로 전송된 {obs_location}에서 발생한 지진", "진도":f"{scale_min} ~ {scale_max}"}
            else:
                log = {"재난": f"지진 {levels}", "날짜": f"{start_date} ~ {end_date}", "위치": f"{main_location} {sub_location}(으)로 전송된 전국에서 발생한 지진", "진도":f"{scale_min} ~ {scale_max}"}
    # 미세먼지
    elif disaster == 3:
        print("미세먼지")
    # 태풍
    elif disaster == 4:
        name = request.args.get("name")
        print("태풍")
    # 홍수
    elif disaster == 5:
        print("홍수")
    # 폭염
    elif disaster == 6:
        print("폭염")
    # 한파
    elif disaster == 7:
        print("한파")
    # 호우
    elif disaster == 8:
        print("호우")
    # 대설
    else:
        print("대설")
    
    print(log)
    return render_template("search.html", log_data=json.dumps(log, ensure_ascii=False))



app.run(host="203.253.25.184", port=8080)

