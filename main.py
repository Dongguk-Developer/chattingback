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
from db_util import user_table,planner

BACK_URL = "https://api.studyhero.kr"
FRONT_URL = "https://studyhero.kr"

KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"

KAKAO_REDIRECT_URI = os.environ['KAKAO_REDIRECT_URI']
KAKAO_CLIENT_ID = os.environ['KAKAO_CLIENT_ID']
KAKAO_CLIENT_SECRET = os.environ['KAKAO_CLIENT_SECRET']
JWT_SECRET = os.environ['JWT_SECRET']


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

session_data = {}
socket_session_data = {}
async def get_current_user(request: Request):
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
def verify_message_token(token: str):
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
def create_message_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    # to_encode.update({"nickname": })
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
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
def read_root():
    return "StudyHero"
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

        # current_user = {"user_id":2032376189} # Depends 종속성 추가 필요
        # user_id = current_user.user_id
        request_data = await request.form()

        mbti = request_data['mbti']
        name = request_data['name']
        age = request_data['age']
        job = request_data['job']
        studyfield = request_data['studyfield']
        xp = request_data['xp']
        print(mbti,name,age,job,studyfield,xp)
        if 'profile_image' in request_data.keys() and request_data['profile_image']:
            file = request_data['profile_image']
            profile_image_path = f"./static/{current_user.user_id}/profile_picture/"+file.filename

            # update_profile->DB에서 user_id를 user_id로 가지는 유저의 정보를 위의 변수로 업데이트

            # 프로필 이미지 저장
            with open(profile_image_path,"wb+") as f:
                f.write(file.file.read())
        else:
            file = None
        update_result = user_table.update_user(user_id=current_user["user_id"],user_nickname=name,user_xp=xp,user_age=age,user_mbti=mbti,user_job=job,user_stuty_field=studyfield)
        if update_result==None:
            return Response(content="update fail 206",status_code=400)
        else:
            return Response(content="updated successfully",status_code=200)
    except Exception as e:
        print(e)
        return Response(content=str(e),status_code=400)


@app.post("/ranking/get")
def get_ranking():
    pass
@app.post("/chatroom/create")
def create_chatroom():
    pass
@app.post("/chatroom/update")
def update_chatroom():
    pass
@app.post("/chatroom/get")
def get_chatroom():
    pass

@app.post("/emoji/create")
def create_emoji():
    pass
@app.post("/emoji/get")
def get_emoji():
    pass


# 캘린더, 플래너 crud
@app.post("/studyplanner/create")
async def create_studyplanner(request:Request):
    current_user=None
    user_id = current_user
    request_data = await request.form()

    planner_id = request_data['planner_id']
    planner_date = request_data['planner_date']
    planner_schedule_name = request_data['planner_schedule_name']
    planner_schedule_status = request_data['planner_schedule_status']
    planner.create_planner(planner_id=planner_id,user_id=2032376189,planner_date=datetime.today(),planner_schedule_name="test",planner_schedule_status="good")
    print()

    # planner_id 고유 번호
    # user_id 외래키
    # planner_date 플래너 일자
    # planner_schedule_name 일정 이름
    # planner_schedule_status 일정 진행 상태
    

    return "good"
@app.post("/studyplanner/update")
# async def create_studyplanner(request:Request,current_user: dict =Depends(get_current_user)):
async def create_studyplanner(request:Request):
    current_user = None
    request_data = await request.form()
    planner_id = request_data['planner_id']
    planner_date = request_data['planner_date']
    planner_schedule_name = request_data['planner_schedule_name']
    planner_schedule_status = request_data['planner_schedule_status']
    planner.update_planner(planner_id=planner_id,planner_date=datetime.today(),planner_schedule_name=planner_schedule_name,planner_schedule_status=planner_schedule_status)
    return "good"
@app.post("/studyplanner/delete")
# async def delete_studyplanner(request:Request,current_user: dict =Depends(get_current_user)):
async def delete_studyplanner(request:Request):
    current_user = None
    request_data = await request.form()
    planner_id = request_data['planner_id']
    # planner_date = request_data['planner_date']
    # planner_schedule_name = request_data['planner_schedule_name']
    # planner_schedule_status = request_data['planner_schedule_status']
    planner.delete_planner(planner_id=planner_id)
    return "good"

@app.post("/calender/create")
def create_calender(request:Request,current_user: dict =Depends(get_current_user)):
    calender_id = ""
    pass
@app.post("/calender/update")
def update_calender(request:Request,current_user: dict =Depends(get_current_user)):
    calender_id = ""
    pass
@app.post("/calender/delete")
def delete_calender(request:Request,current_user: dict =Depends(get_current_user)):
    calender_id = ""
    pass
sio = socketio.AsyncServer(async_mode='asgi')#socketio 서버 생성
app = socketio.ASGIApp(sio, app)#메인 서버와 socketio서버 통합
@sio.on('test')#test 이벤트에 대한 처리
def another_event(sid, data):
    print(sid,data)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ['BACKEND_PORT']),reload=True)