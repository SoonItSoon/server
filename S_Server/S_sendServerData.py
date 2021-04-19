###################################
# Group        : S_Server
# Module       : S_sendServerData
# Purpose      : 모바일 어플리케이션이나 웹 서버에서 보낸 HTTP Method를 분석하고
#                이에 맞는 데이터베이스 쿼리를 작성하여
#                AlertMsgDB나 DisasterDB에서 정보를 가져와 json 형태로 출력한다.
# Final Update : 2020-12-11
####################################

from flask import Flask, render_template, request, Response
import pymysql
import json
import time, datetime, decimal

# 재난 구분 dict
disasterDict = {1: "전염병", 2: "지진", 3: "미세먼지", 4: "태풍", 5: "홍수", 6: "폭염", 7: "한파", 8: "호우", 9: "대설"}
# 재난별 level dict : 전염병(1) 지진(2) 미세먼지(3) 태풍(4) 홍수(5) 폭염(6) 한파(7) 호우(8) 대설(9)
levelDict = {1: {1: "접촉안내", 2: "동선공개", 3: "발생안내", 9: "캠페인"},
                2: {1: "지진", 9: "기타"},
                3: {1: "경보", 2: "주의보", 9: "저감조치"},
                4: {1: "경보", 2: "주의보", 9: "조치알림"},
                5: {1: "경보", 2: "주의보", 9: "조치알림"},
                6: {1: "경보", 2: "주의보", 9: "기타"},
                7: {1: "경보", 2: "주의보", 9: "기타"},
                8: {1: "경보", 2: "주의보", 9: "기타"},
                9: {1: "경보", 2: "주의보", 9: "기타"}}
# 재난 테이블 dict
AlertMsgDBDict = {0: "AM", 1: "PD", 2: "EQ", 3: "FD", 4: "TP", 5: "FL", 6: "HW", 7: "CW", 8: "HR", 9: "HS"}

# 요청 횟수
reqCnt = 0

# datetime을 json화 시키기 위한 함수
def json_default(value):
    # 참고 : https://dgkim5360.tistory.com/entry/not-JSON-serializable-error-on-python-json
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, decimal.Decimal):
        return float(value)
    else:
        print(f"json_default error : {value} ({type(value)})")
        raise TypeError("not JSON serializable")


# 서버
app = Flask("SoonItSoon Server")

# 서버 접속 테스트용 root
@app.route("/")
def home():
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(f"{now_date} [S_sendServerData] REST connection request")
    return render_template("home.html")

# 재난문자 검색
@app.route("/search")
def search():
    global reqCnt
    reqCnt += 1
    # 성능 측정 및 로그용 시간
    start_time = time.time()
    # 현재 시각
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
    # AlertMsgDB 접근 변수
    AlertMsgDB = pymysql.connect(
        user='kyeol',
        passwd='hee',
        host='127.0.0.1',
        db='AlertMsgDB',
        charset='utf8'
    )
    AlertMsgDB_cursor = AlertMsgDB.cursor(pymysql.cursors.DictCursor)
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
    sql_AMall = f"SELECT * FROM AM WHERE (send_date BETWEEN '{start_date}' AND '{end_date}') AND disaster = {disaster}"
    if inner_text:
        sql_AMall += f" AND msg like '%{inner_text}%'"
    if sub_location == "전체":
        sql_AMloc = f"{sql_AMall} AND (send_location LIKE '%{main_location}%')"
    else:
        sql_AMloc = f"{sql_AMall} AND (send_location LIKE '%{main_location} {sub_location}%' OR send_location LIKE '%{main_location} 전체%')"
    # SQL 쿼리와 로그
    sql = ""
    log_default = f"{now_date} [S_sendServerData]"
    log = f"{log_default} REST Search Request (Request Cnt : {reqCnt})\n"

    # 전염병(1) 태풍(4)
    if disaster in [1, 4]:
        # 전염병 이름
        name = request.args.get("name")
        if name:
            sql_multi = f"SELECT * FROM {AlertMsgDBDict[disaster]} WHERE name = '{name}' AND level IN ({level})"
        else:
            sql_multi = f"SELECT * FROM {AlertMsgDBDict[disaster]} WHERE level IN ({level})"
        log += f"{log_default} disaster : {disasterDict[disaster]} {name} | level : {levels} | date : {start_date} ~ {end_date} | "
        if main_location and sub_location:
            sql = f"SELECT * FROM ({sql_AMloc}) AS AM JOIN ({sql_multi}) AS {AlertMsgDBDict[disaster]} USING (mid)"
            log += f"location : {main_location} {sub_location} | "
        else:
            sql = f"SELECT * FROM ({sql_AMall}) AS AM JOIN ({sql_multi}) AS {AlertMsgDBDict[disaster]} USING (mid)"
            log += f"location : 전체 | "
    # 지진(2)
    elif disaster == 2:
        # 최소/최대 규모
        scale_min = float(request.args.get("scale_min"))
        scale_max = float(request.args.get("scale_max"))
        # 관측 위치
        obs_location = request.args.get("obs_location")

        sql_EQ = f"SELECT * FROM EQ WHERE level IN ({level}) AND (scale BETWEEN {scale_min} AND {scale_max} OR scale IS NULL)"
        log += f"{log_default} disaster : {disasterDict[disaster]} | level : {levels} | date : {start_date} ~ {end_date} | "
        if main_location and sub_location:
            sql = f"SELECT * FROM ({sql_AMloc}) AS AM JOIN ({sql_EQ}) AS EQ USING (mid)"
            log += f"location : {main_location} {sub_location} | "
        else:
            sql = f"SELECT * FROM ({sql_AMall}) AS AM JOIN ({sql_EQ}) AS EQ USING (mid)"
            log += f"location : 전체 | "
        if obs_location:
            sql += f" WHERE EQ.obs_location = '{obs_location}' OR EQ.obs_location IS NULL"
            log += f"scale : {scale_min} ~ {scale_max} | obs_location : {obs_location} | "
        else:
            log += f"scale : {scale_min} ~ {scale_max} | obs_location : 전체 | "
    # 미세먼지(3) 홍수(5) 폭염(6) 한파(7) 호우(8) 대설(9)
    elif disaster in [3, 5, 6, 7, 8, 9]:
        sql_multi = f"SELECT * FROM {AlertMsgDBDict[disaster]} WHERE level IN ({level})"
        log += f"{log_default} disaster : {disasterDict[disaster]} | level : {levels} | date : {start_date} ~ {end_date} | "
        if main_location and sub_location:
            sql = f"SELECT * FROM ({sql_AMloc}) AS AM JOIN ({sql_multi}) AS {AlertMsgDBDict[disaster]} USING (mid)"
            log += f"location : {main_location} {sub_location} | "
        else:
            sql = f"SELECT * FROM ({sql_AMall}) AS AM JOIN ({sql_multi}) AS {AlertMsgDBDict[disaster]} USING (mid)"
            log += f"location : 전체 | "
    
    if inner_text:
        log += f"inner_text : {inner_text}\n"
    else:
        log += f"inner_text : none\n"
    sql += " ORDER BY AM.mid DESC LIMIT 100;"
    log += f"{log_default} DB query : {sql}\n"
    
    AlertMsgDB_cursor.execute(sql)
    result = AlertMsgDB_cursor.fetchall()
    jsonAll = dict(zip(range(1, len(result) + 1), result))

    log += f"{log_default} DB result : {len(result)} results | "
    end_time = time.time()
    log += f"Process Time : {(end_time-start_time):.3f}s"
    print(log)
    res = Response(json.dumps(jsonAll, default=json_default, ensure_ascii=False), content_type="application/json; charset=utf-8");
    res.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    return res

# 재난문자 검색
@app.route("/count")
def count():
    global reqCnt
    reqCnt += 1
    # 성능 측정 및 로그용 시간
    start_time = time.time()
    # 현재 시각
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
    # AlertMsgDB 접근 변수
    AlertMsgDB = pymysql.connect(
        user='kyeol',
        passwd='hee',
        host='127.0.0.1',
        db='AlertMsgDB',
        charset='utf8'
    )
    AlertMsgDB_cursor = AlertMsgDB.cursor(pymysql.cursors.DictCursor)
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
    if level:
        req_levels = level.split(",")
        for req_level in req_levels:
            levels += levelDict[disaster][int(req_level)] + " "

    # AM 테이블 쿼리
    sql_AMall = f"SELECT * FROM AM WHERE (send_date BETWEEN '{start_date}' AND '{end_date}') AND disaster = {disaster}"
    if sub_location == "전체":
        sql_AMloc = f"{sql_AMall} AND (send_location LIKE '%{main_location}%')"
    else:
        sql_AMloc = f"{sql_AMall} AND (send_location LIKE '%{main_location} {sub_location}%' OR send_location LIKE '%{main_location} 전체%')"
    # SQL 쿼리와 로그
    sql = ""
    log_default = f"{now_date} [S_sendServerData]"
    log = f"{log_default} REST Count Request (Request Cnt : {reqCnt})\n"
    if disaster == 0:
        sql = f"SELECT COUNT(*) FROM AM WHERE send_date BETWEEN '{start_date}' AND '{end_date}'"
    # 전염병(1) 태풍(4)
    elif disaster in [1, 4]:
        # 전염병 이름
        name = request.args.get("name")
        if name:
            sql_multi = f"SELECT * FROM {AlertMsgDBDict[disaster]} WHERE name = '{name}' AND level IN ({level})"
        else:
            sql_multi = f"SELECT * FROM {AlertMsgDBDict[disaster]} WHERE level IN ({level})"
        log += f"{log_default} disaster : {disasterDict[disaster]} {name} | level : {levels} | date : {start_date} ~ {end_date} | "
        if main_location and sub_location:
            sql = f"SELECT COUNT(*) FROM ({sql_AMloc}) AS AM JOIN ({sql_multi}) AS {AlertMsgDBDict[disaster]} USING (mid)"
            log += f"location : {main_location} {sub_location}\n"
        else:
            sql = f"SELECT COUNT(*) FROM ({sql_AMall}) AS AM JOIN ({sql_multi}) AS {AlertMsgDBDict[disaster]} USING (mid)"
            log += f"location : 전체\n"
    # 지진(2)
    elif disaster == 2:
        # 최소/최대 규모
        scale_min = float(request.args.get("scale_min"))
        scale_max = float(request.args.get("scale_max"))
        # 관측 위치
        obs_location = request.args.get("obs_location")

        sql_EQ = f"SELECT * FROM EQ WHERE level IN ({level}) AND (scale BETWEEN {scale_min} AND {scale_max} OR scale IS NULL)"
        log += f"{log_default} disaster : {disasterDict[disaster]} | level : {levels} | date : {start_date} ~ {end_date} | "
        if main_location and sub_location:
            sql = f"SELECT COUNT(*) FROM ({sql_AMloc}) AS AM JOIN ({sql_EQ}) AS EQ USING (mid)"
            log += f"location : {main_location} {sub_location} | "
        else:
            sql = f"SELECT COUNT(*) FROM ({sql_AMall}) AS AM JOIN ({sql_EQ}) AS EQ USING (mid)"
            log += f"location : 전체 | "
        if obs_location:
            sql += f" WHERE EQ.obs_location = '{obs_location}' OR EQ.obs_location IS NULL"
            log += f"scale : {scale_min} ~ {scale_max} | obs_location : {obs_location}\n"
        else:
            log += f"scale : {scale_min} ~ {scale_max} | obs_location : 전체\n"
    # 미세먼지(3) 홍수(5) 폭염(6) 한파(7) 호우(8) 대설(9)
    elif disaster in [3, 5, 6, 7, 8, 9]:
        sql_multi = f"SELECT * FROM {AlertMsgDBDict[disaster]} WHERE level IN ({level})"
        log += f"{log_default} disaster : {disasterDict[disaster]} | level : {levels} | date : {start_date} ~ {end_date} | "
        if main_location and sub_location:
            sql = f"SELECT COUNT(*) FROM ({sql_AMloc}) AS AM JOIN ({sql_multi}) AS {AlertMsgDBDict[disaster]} USING (mid)"
            log += f"location : {main_location} {sub_location}\n"
        else:
            sql = f"SELECT COUNT(*) FROM ({sql_AMall}) AS AM JOIN ({sql_multi}) AS {AlertMsgDBDict[disaster]} USING (mid)"
            log += f"location : 전체\n"
    if disaster != 0:
        sql += " ORDER BY AM.mid DESC LIMIT 100;"
    log += f"{log_default} DB query : {sql}\n"
    
    AlertMsgDB_cursor.execute(sql)
    result = AlertMsgDB_cursor.fetchall()
    jsonAll = dict(zip(range(1, len(result) + 1), result))

    log += f"{log_default} DB result : {len(result)} results | "
    end_time = time.time()
    log += f"Process Time : {(end_time-start_time):.3f}s"
    print(log)
    return Response(json.dumps(jsonAll, default=json_default, ensure_ascii=False), content_type="application/json; charset=utf-8");


# 서버 run
app.run(host="203.253.25.184", port=8080)
