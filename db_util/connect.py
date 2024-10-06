import pymysql
# DB에 접근하는 conn, cur 객체 생성 후 반환
def mysql_create_session():
    conn = pymysql.connect(host='api.studyhero.kr', user='studyhero-db', password='!Studyhero-db',port=3306, db='studyhero-db', 
                            charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    return conn, cur