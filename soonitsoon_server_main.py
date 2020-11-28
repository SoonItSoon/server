##################################
# ------Project SoonItSoon------ #
# Team         : SoonItSoon      #
# Dev. Part    : Server          #
# Dev. Member  : SoonWook Park,  #
#                HyeYoon Jeon    #
# Dev. Term    : 2020-2 ~ 2021-1 #
# Dev. Start   : 2020-11-14      #
# Final Update : 2020-11-28      #
##################################

# S_Background.S_mainBackground 모듈
import S_Background.S_mainBackground

# S_Server.S_sendServerData 모듈
import S_Server.S_sendServerData


# AlertMsgDB 접근 변수
AlertMsgDB = pymysql.connect(
     user='kyeol',
     passwd='hee',
     host='127.0.0.1',
     db='AlertMsgDB',
     charset='utf8'
)
AlertMsgDB_cursor = AlertMsgDB.cursor(pymysql.cursors.DictCursor)