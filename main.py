from fastapi.middleware.cors import CORSMiddleware
import os
import socketio
from fastapi.responses import RedirectResponse,HTMLResponse,JSONResponse
import requests
from datetime import datetime, timedelta
from jose import JWTError, jwt
from jose.exceptions import *
from uuid import uuid4
import uvicorn
from fastapi import FastAPI,Request,WebSocket,Response,Depends,HTTPException
from fastapi import Cookie
from typing import Optional,Union
import logging
import httpx
import time
import random
from db_util import calender
from db_util import chatting_room
from db_util import hashtag
from db_util import kakao_api
from db_util import message_image,message_read,message_text,message_video,message_voice,message
from db_util import planner
from db_util import profile_image
from db_util import room_users
from db_util import user_table
import sys
DEV_MODE = True


BACK_URL = ""
FRONT_URL = ""
if DEV_MODE:
    BACK_URL = "http://localhost:8090"
    FRONT_URL = "http://localhost:3000"
else:
    BACK_URL = "https://api.studyhero.kr"
    FRONT_URL = "https://studyhero.kr"

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

if DEV_MODE:
    os.environ['KAKAO_REDIRECT_URI']=''
    os.environ['KAKAO_CLIENT_ID']=''
    os.environ['KAKAO_CLIENT_SECRET']=''
    os.environ['JWT_SECRET']=''
    os.environ['BACKEND_PORT']='8090'

KAKAO_REDIRECT_URI = os.environ['KAKAO_REDIRECT_URI']
KAKAO_CLIENT_ID = os.environ['KAKAO_CLIENT_ID']
KAKAO_CLIENT_SECRET = os.environ['KAKAO_CLIENT_SECRET']
JWT_SECRET = os.environ['JWT_SECRET']


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

session_data = {}
socket_session_data = {}
SWAGGER_HEADERS = {
    "title": "SWAGGER UI 변경 테스트",
    "version": "100.100.100",
    "description": "## SWAGGER 문서 변경 \n - swagger 문서를 변경해보는 테스트입니다. \n - 테스트 1234 \n - 테스트 5678",
    "contact": {
        "name": "CHAECHAE",
        "url": "https://chaechae.life",
        "email": "chaechae.couple@gmail.com",
        "license_info": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
    },
}
async def get_current_user(request: Request):
    return {"user_id":2032376189}
    sessionid = request.cookies.get("sessionid")
    
    if sessionid==None or not sessionid in session_data.keys():
        raise HTTPException(status_code=404, detail="로그인 정보가 없습니다.")
    user_id = session_data[sessionid]['user_id']
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    db = mysql_create_session()
    cursor = db[1]
    # if session_data[sessionid]["expire"]<time.time():
    #     cursor.execute("SELECT kakao_access_token,kakao_refresh_token FROM kakao_api WHERE kakao_id = %s", (user_id,))
    #     kakao_access_token,kakao_refresh_token = cursor.fetchone()
    #     refresh_access_token(kakao_refresh_token)
    try:
        

        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return user
    except Exception as e:
        print(e)
        raise e
def generate_session_id():
    return str(uuid4())
def verify_access_token(token: str):
    if token=="":
        return None
    try:
        payload = jwt.decode(token=token,key= JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        return e
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, KAKAO_CLIENT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt
def refresh_access_token(refresh_token):
    grant_type = "refresh_token"
    client_id = KAKAO_CLIENT_ID
    client_secret = KAKAO_CLIENT_SECRET
    header = {"Content-type": "application/x-www-form-urlencoded;charset=utf-8"}
    data={
                "grant_type": grant_type,
                "client_id": KAKAO_CLIENT_ID,
                "refresh_token": refresh_token,
                "client_secret": KAKAO_CLIENT_SECRET,
            }
    """
    grant_type  String  refresh_token으로 고정                              O
    client_id   String  앱 REST API 키
                [내 애플리케이션] > [앱 키]에서 확인 가능                  O
    refresh_token   String  토큰 발급 시 응답으로 받은 refresh_token
                    Access Token을 갱신하기 위해 사용                        O
    client_secret   String  토큰 발급 시, 보안을 강화하기 위해 추가 확인하는 코드
                    [내 애플리케이션] > [카카오 로그인] > [보안]에서 설정 가능
                    ON 상태인 경우 필수 설정해야 함                         X
    """
    res = requests.post("https://kauth.kakao.com/oauth/token",headers=header,data=data)
    print(res.json())
    # https://kauth.kakao.com/oauth/token
def parse_cookie(data):
    result = {}
    if data==None:
        return result
    try:
        for cookie in data.split("; "):
            if cookie[len(cookie.split("=")[0]):][0]=='=':
                result[cookie.split("=")[0]] = cookie[len(cookie.split("=")[0])+1:]
            else:
                result[cookie.split("=")[0]] = cookie[len(cookie.split("=")[0]):]
    except:
        pass
    return result
origins = [
    BACK_URL,
    FRONT_URL,
]
app = FastAPI(swagger_ui_parameters={
        "deepLinking": True,
        "displayRequestDuration": True,
        "docExpansion": "none",
        "operationsSorter": "method",
        "filter": True,
        "tagsSorter": "alpha",
        "syntaxHighlight.theme": "tomorrow-night",
    },
    **SWAGGER_HEADERS)
logging.basicConfig(level=logging.INFO)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_user_by_sessionid(sessionid):
    
    if not sessionid in session_data.keys():
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user_id = session_data[sessionid]['user_id']
    user = user_table.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user
    
@app.get("/")
def read_root():
    return "StudyHero"
@app.post("/test")
def test_root():
    return {"data":"StudyHero"}
# 유저 객체를 전달함
@app.post("/profile/get")
async def get_profile(request: Request,current_user:dict=Depends(get_current_user)):
    if current_user==None:
        raise HTTPException(status_code=404, detail="로그인 정보가 없습니다.")
    try:        
        if not current_user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return current_user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
@app.post("/profile/update")
async def update_profile(request: Request,current_user:dict=Depends(get_current_user)):
    try:
        user_id = current_user['user_id']
        request_data = await request.form()

        mbti = request_data['mbti']
        name = request_data['name']
        age = request_data['age']
        job = request_data['job']
        studyfield = request_data['studyfield']
        xp = request_data['xp']
        if 'profile_image' in request_data.keys() and request_data['profile_image']:
            file = request_data['profile_image']
            profile_image_path = f"./static/{current_user.user_id}/profile_picture/"+file.filename

            # update_profile->DB에서 user_id를 user_id로 가지는 유저의 정보를 위의 변수로 업데이트

            # 프로필 이미지 저장
            with open(profile_image_path,"wb+") as f:
                f.write(file.file.read())
        else:
            file = None
        update_result = user_table.update_user(user_id=user_id,user_nickname=name,user_xp=xp,user_age=age,user_mbti=mbti,user_job=job,user_stuty_field=studyfield)
        if update_result==None:
            return Response(content="update fail 206",status_code=400)
        else:
            return Response(content="updated successfully",status_code=200)
    except Exception as e:
        print(e)
        return Response(content=str(e),status_code=400)


@app.post("/ranking/get")
def get_ranking(request:Request,current_user:dict=Depends(get_current_user)):
    pass

@app.post("/chatroom/create")
def create_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
    pass
@app.post("/chatroom/update")
def update_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
    pass
@app.post("/chatroom/get")
def get_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
    pass
@app.post("/chatroom/get")
def delete_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
    pass

@app.post("/emoji/create")
def create_emoji():
    pass
@app.post("/emoji/get")
def get_emoji():
    pass

# 캘린더, 플래너 crud
@app.post("/studyplanner/get")
async def get_studyplanner(request:Request,current_user:dict=Depends(get_current_user)):
    user_id = current_user['user_id']
    request_data = await request.form()
    planner_id = request_data['planner_id']

    return planner.get_planner_by_id(planner_id=planner_id)
# 캘린더, 플래너 crud
@app.post("/studyplanner/create")
async def create_studyplanner(request:Request,current_user:dict=Depends(get_current_user)):
    try:
        user_id = current_user['user_id']
        request_data = await request.form()

        planner_id = request_data['planner_id']
        planner_date = request_data['planner_date']
        planner_schedule_name = request_data['planner_schedule_name']
        planner_schedule_status = request_data['planner_schedule_status']
        planner.create_planner(planner_id=planner_id,user_id=user_id,planner_date=datetime.today(),planner_schedule_name=planner_schedule_name,planner_schedule_status=planner_schedule_status)
        return Response(content="Studyplanner Created Successfully",status_code=201)
    except:
        return Response(content="Studyplanner Create Something Wrong",status_code=417)
@app.post("/studyplanner/update")
async def update_studyplanner(request:Request,current_user: dict=Depends(get_current_user)):
    try:
        request_data = await request.form()
        planner_id = request_data['planner_id']
        planner_date = request_data['planner_date']
        planner_schedule_name = request_data['planner_schedule_name']
        planner_schedule_status = request_data['planner_schedule_status']
        planner.update_planner(planner_id=planner_id,planner_date=datetime.strptime(planner_date,"%Y-%m-%d").date(),planner_schedule_name=planner_schedule_name,planner_schedule_status=planner_schedule_status)
        return Response(content="Studyplanner Updated Successfully",status_code=201)
    except:
        return Response(content="Studyplanner Update Something Wrong",status_code=417)
@app.post("/studyplanner/delete")
async def delete_studyplanner(request:Request,current_user: dict =Depends(get_current_user)):
    try:
        request_data = await request.form()
        planner_id = request_data['planner_id']
        planner.delete_planner(planner_id=planner_id)
        return Response(content="Studyplanner Deleted Successfully",status_code=200)
    except:
        return Response(content="Studyplanner Delete Something Wrong",status_code=417)

@app.post("/calender/create")
async def create_calender(request:Request,current_user: dict =Depends(get_current_user)):
    try:
        request_data = await request.form()
        planner_id = request_data['planner_id']
        planner.delete_planner(planner_id=planner_id)
        return Response(content="Studyplanner Deleted Successfully",status_code=200)
    except:
        return Response(content="Studyplanner Delete Something Wrong",status_code=417)
@app.post("/calender/update")
async def update_calender(request:Request,current_user: dict =Depends(get_current_user)):
    try:
        request_data = await request.form()
        planner_id = request_data['planner_id']
        planner.delete_planner(planner_id=planner_id)
        return Response(content="Studyplanner Deleted Successfully",status_code=200)
    except:
        return Response(content="Studyplanner Delete Something Wrong",status_code=417)
@app.post("/calender/delete")
async def delete_calender(request:Request,current_user: dict =Depends(get_current_user)):
    try:
        request_data = await request.form()
        planner_id = request_data['planner_id']
        planner.delete_planner(planner_id=planner_id)
        return Response(content="Studyplanner Deleted Successfully",status_code=200)
    except:
        return Response(content="Studyplanner Delete Something Wrong",status_code=417)
sio = socketio.AsyncServer(async_mode='asgi',cors_allowed_origins=origins) #socketio 서버 생성
app = socketio.ASGIApp(sio, app) #메인 서버와 socketio서버 통합

@sio.on('message')
async def send_message(sid, data):
    room = data.get("room_code")
    message = data.get("message")
    sessionid = socket_session_data[sid]['sessionid']
    if (not sessionid) or (not (sessionid in session_data.keys())):
        print("Invalid or expired token")
        await sio.emit("redirect", {"url": "/login"}, room=room)
        return
    user_id = get_user_by_sessionid(sessionid)['user_id']
    user_nickname = get_user_by_sessionid(sessionid)['user_nickname']
    await sio.emit("receive_message", {
        "user_id": user_id,
        "message": message,
        "user_nickname":user_nickname
    }, room=room)
    return
@sio.event
async def connect(sid, environ, auth):
    try:
        room = auth.get("room")  # room 정보 가져오기
        cookies = parse_cookie(environ.get('HTTP_COOKIE'))
        sessionid = cookies.get('sessionid')
        session_data[sessionid]['sid'] = sid
        socket_session_data[sid] = {'sessionid':sessionid}
    except:
        await sio.disconnect(sid)
    try:
        payload = get_user_by_sessionid(sessionid)
        del payload['user_create']
        del payload['user_update']
        if cookies and sessionid:
            if room:  # room 정보가 있으면 클라이언트를 해당 room에 참여시킴
                await sio.enter_room(sid, room)
                await sio.emit("connect_success", data={"user": payload, "message": f"Connected to room {room}!", "sessionid": sessionid}, room=sid)
            else: # room 정보가 없는 곳 접속
                await sio.emit("redirect", {"url": "/"}, room=room)
        else:
            print("Unauthorized connection attempt.")
            await sio.disconnect(sid)
    except Exception as e:
        print(e)
        await sio.emit("refresh", room=sid) 
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ['BACKEND_PORT']),reload=DEV_MODE)