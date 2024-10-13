from typing import Union
import uvicorn
from fastapi import FastAPI,Request,WebSocket
from fastapi.middleware.cors import CORSMiddleware
import os
import pymysql
import logging
# from db_util.queryCheck import query_check
# from db_util.connect import mysql_create_session
import socketio
import httpx
from fastapi.responses import RedirectResponse
import requests

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

@app.post("/create_emoji")
def create_emoji():
    pass
@app.post("/get_emoji")
def get_emoji():
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

# 카카오 OAuth 키 값 자리


@app.get("/auth/kakao")
async def auth_kakao():
    print(f"{KAKAO_AUTH_URL}?client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code")
    return RedirectResponse(
        url=f"{KAKAO_AUTH_URL}?client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code"
    )

@app.get("/auth/kakao/callback")
async def auth_kakao_callback(code: str):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            KAKAO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_CLIENT_ID,
                "redirect_uri": KAKAO_REDIRECT_URI,
                "code": code,
                "client_secret": KAKAO_CLIENT_SECRET,
            },
        )
        token_response_data = token_response.json()
        access_token = token_response_data.get("access_token")

    if access_token:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                KAKAO_USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_data = user_response.json()
            return user_data

    return {"error": "인증 실패"}

@app.get("/oauth/kakao/callback")
def oauth_callback(code:str):
    payload = {"grant_type": "authorization_code",
               "client_id": KAKAO_CLIENT_ID,
               "redirect_uri": KAKAO_REDIRECT_URI,
               "code": code,
               "client_secret": KAKAO_CLIENT_SECRET}
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    req = requests.post("https://kauth.kakao.com/oauth/token",data=payload,headers=headers)

sio = socketio.AsyncServer(async_mode='asgi') #socketio 서버 생성
app = socketio.ASGIApp(sio, app) #메인 서버와 socketio서버 통합
@sio.on('message') #message 이벤트에 대한 처리
def another_event(sid, data):
    print(sid,data)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ['BACKEND_PORT']),reload=True)