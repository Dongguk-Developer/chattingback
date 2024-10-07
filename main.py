from typing import Union
import uvicorn
from fastapi import FastAPI,Request,WebSocket
from fastapi.middleware.cors import CORSMiddleware
import os
import pymysql
import logging
from db_util.queryCheck import query_check
from db_util.connect import mysql_create_session
import socketio
origins = [
    "https://api.studyhero.kr",
    "https://studyhero.kr",
]
app = FastAPI()
logging.basicConfig(level=logging.INFO)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root(request:Request):
    return {"Hello": "World"}
@app.post("/get_profile")
def get_profile():
    pass
@app.post("/update_profile")
def update_profile():
    pass

@app.post("/get_ranking")
def get_ranking():
    pass
@app.post("/create_chatroom")
def create_chatroom():
    pass
@app.post("/update_chatroom")
def update_chatroom():
    pass
@app.post("/get_chatroom")
def get_chatroom():
    pass

@app.post("/create_imoji")
def create_imoji():
    pass
@app.post("/get_imoji")
def get_imoji():
    pass

@app.post("/create_studyplanner")
def create_studyplanner():
    pass
@app.post("/update_studyplanner")
def create_studyplanner():
    pass
@app.post("/delete_studyplanner")
def delete_studyplanner():
    pass

@app.post("/create_calender")
def create_calender():
    pass
@app.post("/update_calender")
def update_calender():
    pass
@app.post("/delete_calender")
def delete_calender():
    pass
@app.get("/test")
def get_test_res():
    conn, cur = mysql_create_session() 
    try:
        sql = "SELECT * FROM user"
        cur.execute(sql)
        row = cur.fetchone()
    finally:
        conn.close()
    return row
sio = socketio.AsyncServer(async_mode='asgi')#socketio 서버 생성
app = socketio.ASGIApp(sio, app)#메인 서버와 socketio서버 통합
@sio.on('test')#test 이벤트에 대한 처리
def another_event(sid, data):
    print(sid,data)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ['BACKEND_PORT']),reload=True)