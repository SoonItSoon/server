#################################
# Group        : S_Server
# Module       : S_sendServerData
# Purpose      : 모바일 어플리케이션이나 웹 서버에서 보낸 HTTP Method를 분석하고
#                이에 맞는 데이터베이스 쿼리를 작성하여
#                AlertMsgDB나 DisasterDB에서 정보를 가져와 json 형태로 출력한다.
# Final Update : 2020-11-28
##################################

from flask import Flask, render_template, request
import datetime
import time
import json
import pymysql

# AlertMsgDB 접근 변수
AlertMsgDB = pymysql.connect(
     user='kyeol',
     passwd='hee',
     host='127.0.0.1',
     db='AlertMsgDB',
     charset='utf8'
)
AlertMsgDB_cursor = AlertMsgDB.cursor(pymysql.cursors.DictCursor)

# 재난별 level dict : 전염병(1) 지진(2) 미세먼지(3) 태풍(4) 홍수(5) 폭염(6) 한파(7) 호우(8) 대설(9)
levelDict = {1: {1: "접촉안내", 2: "동선공개", 3: "발생안내", 9: "캠페인"},
                2: {1: "지진", 9: "기타"},
                3: {1: "경보", 2: "주의보", 9: "저감조치"},
                4: {1: "경보", 2: "주의보", 9: "조치조치"},
                5: {1: "경보", 2: "주의보", 9: "조치알림"},
                6: {1: "경보", 2: "주의보", 9: "기타"},
                7: {1: "경보", 2: "주의보", 9: "기타"},
                8: {1: "경보", 2: "주의보", 9: "기타"},
                9: {1: "경보", 2: "주의보", 9: "기타"}}

# datetime을 json화 시키기 위한 함수
# 참고 : https://dgkim5360.tistory.com/entry/not-JSON-serializable-error-on-python-json
def json_default(value):
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%s")
    raise TypeError("not JSON serializable")

# 서버
app = Flask("SoonItSoon Server")

# 서버 접속 테스트용 root
@app.route("/")
def home():
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(f"[{now_date} S_sendServerData] REST connection request")
    return render_template("home.html")

# 재난문자 검색
@app.route("/search")
def search():
    # 현재 시각
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # 시작 날짜
    start_date = request.args.get("start_date")
    # 종료 날짜 (default : 현재 시각)
    end_date = request.args.get("end_date")
    if not end_date:
        end_date = now_date
    # 시/도, 시/군/구 (default : 전체)
    main_location = request.args.get("main_location")
    sub_location = request.args.get("sub_location")
    # 재난 구분 (전염병(1) 지진(2) 미세먼지(3) 태풍(4) 홍수(5) 폭염(6) 한파(7) 호우(8) 대설(9))
    disaster = int(request.args.get("disaster"))
    # 등급 (재난별 등급은 levelDict 참조)
    level = request.args.get("level")
    levels = ""
    req_levels = level.split(",")
    for req_level in req_levels:
        levels += levelDict[disaster][int(req_level)] + " "
    # 텍스트 검색 (default : none)
    inner_text = request.args.get("inner_text")

    # AM 테이블 쿼리
    sql_AMall = f"SELECT * FROM AM WHERE send_date BETWEEN '{start_date}' AND '{end_date}' AND disaster = {disaster}"
    sql_AMloc = f"{sql_AMall} AND (send_location LIKE '%{main_location} {sub_location}%' OR send_location LIKE '%{main_location} 전체%')"
    # SQL 쿼리와 로그
    sql = ""
    log = f"[{now_date} S_sendServerData] REST search request\n"
    # 전염병(1)
    if disaster == 1:
        name = request.args.get("name")
        sql_PD = f"SELECT * FROM PD WHERE name = '{name}' AND level IN ({level})"
        log += f"disaster : 전염병 {name}\nlevel : {levels}\ndate : {start_date} ~ {end_date}\n"
        if main_location and sub_location:
            sql = f"SELECT * FROM ({sql_AMloc}) AS AM JOIN ({sql_PD}) AS PD"
            log += f"location : {main_location} {sub_location}\n"
        else:
            sql = f"SELECT * FROM ({sql_AMall}) AS AM JOIN ({sql_PD}) AS PD"
            log += "location : 전체\n"
        
        if inner_text:
            sql += f" WHERE AM.msg like '%{inner_text}%'"
            log += f"inner_text : {inner_text}\n"
        else:
            log += "inner_text : none\n"
        sql += " ORDER BY AM.mid DESC LIMIT 100;"
        log += f"DB query : {sql}"
    # 지진(2)
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
    # 미세먼지(3)
    elif disaster == 3:
        print("미세먼지")
    # 태풍(4)
    elif disaster == 4:
        name = request.args.get("name")
        print("태풍")
    # 홍수(5)
    elif disaster == 5:
        print("홍수")
    # 폭염(6)
    elif disaster == 6:
        print("폭염")
    # 한파(7)
    elif disaster == 7:
        print("한파")
    # 호우(8)
    elif disaster == 8:
        print("호우")
    # 대설(9)
    else:
        print("대설")
    
    if not sql:
        sql = f"SELECT * FROM alertMsg WHERE date BETWEEN '{start_date}' AND '{end_date}';"
    AlertMsgDB_cursor.execute(sql)
    result = AlertMsgDB_cursor.fetchall()
    jsonAll = dict(zip(range(1, len(result) + 1), result))

    print(log)
    # all_data = {"log_data": json.dumps(log, default=json_default, ensure_ascii=False), "db_data": json.dumps(jsonAll, default=json_default, ensure_ascii=False)}
    return render_template("search.html", all_data=json.dumps(jsonAll, default=json_default, ensure_ascii=False))
# return render_template("search.html", all_data=json.dumps(all_data, ensure_ascii=False))

# 서버 run
app.run(host="203.253.25.184", port=8080)

