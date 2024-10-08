from . import connect
def get_user_information(user_id):
    con, cur = connect.mysql_create_session()
    cur.execute("SELECT * FROM user WHERE user_id=%d", (user_id))
    return cur.fetchone()