import pymysql
import os
# DB에 접근하는 conn, cur 객체 생성 후 반환
def mysql_create_session():
    conn = pymysql.connect(host=os.environ['DB_HOST'], user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],port=os.environ['DB_PORT'], db=os.environ['DB_NAME'], 
                            charset='utf8', cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    return conn, cur
    # 2024200200 여기 보안 부분 고쳐야함(os.environ쓰고 아직 커밋 안함)