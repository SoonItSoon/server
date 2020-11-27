from flask import Flask, render_template, request

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
    level = request.args.get("level")
    inner_text = request.args.get("inner_text")
    print(f"{start_date}, {end_date}, {main_location}, {sub_location}, {disaster}, {level}, {inner_text}")

    # 전염병
    if disaster == 1:
        name = request.args.get("name")
        req_levels = level.split(",")
        levels = []
        for req_level in req_levels:
            levels.append(levelDict[disaster][int(req_level)])
        if inner_text:
            print(f"[S_sendServerData]{disaster} {name} {levels}/{start_date}~{end_date}/{main_location} {sub_location}/{inner_text}")
        else:
            print(f"[S_sendServerData]{disaster} {name} {levels}/{start_date}~{end_date}/{main_location} {sub_location}")
    # 지진
    elif disaster == 2:
        print("지진")
    # 미세먼지
    elif disaster == 3:
        print("미세먼지")
    # 태풍
    elif disaster == 4:
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
    return render_template("home.html")



app.run(host="203.253.25.184", port=8080)

