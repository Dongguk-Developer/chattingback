from typing import Union
import uvicorn
from fastapi import FastAPI,Request,WebSocket
from fastapi.middleware.cors import CORSMiddleware
import os
import pymysql
import logging
from db_util.queryCheck import query_check
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

# 웹소켓 연결
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f"client connected : {websocket.client}")
    await websocket.accept() # client의 websocket접속 허용
    await websocket.send_text(f"Welcome client : {websocket.client}")
    while True:
        data = await websocket.receive_text()  # client 메시지 수신대기
        print(f"message received : {data} from : {websocket.client}")
        await websocket.send_text(f"Message text was: {data}") # client에 메시지 전달
@app.websocket("/sendMessage")
async def websocket_endpoint(websocket: WebSocket):
    print(f"client connected : {websocket.client}")
    await websocket.accept() # client의 websocket접속 허용
    await websocket.send_text(f"Welcome client : {websocket.client}")
    while True:
        data = await websocket.receive_text()  # client 메시지 수신대기
        print(f"message received : {data} from : {websocket.client}")
        await websocket.send_text(f"Message text was: {data}") # client에 메시지 전달

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=os.environ['BACKEND_PORT'],reload=True)