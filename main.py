from typing import Union
import uvicorn
from fastapi import FastAPI, Request, WebSocket,Response,Depends,HTTPException
from fastapi import Cookie
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import os
import pymysql
import logging
# from db_util.queryCheck import query_check
from db_util.connect import mysql_create_session
import socketio
import httpx
from fastapi.responses import RedirectResponse,HTMLResponse,JSONResponse
import requests
from datetime import datetime, timedelta
from jose import JWTError, jwt
from jose.exceptions import *
import time
import random
from uuid import uuid4

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

# # CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # React 애플리케이션 도메인
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_user_by_sessionid(sessionid):
    db = mysql_create_session()
    if not sessionid in session_data.keys():
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user_id = session_data[sessionid]['user_id']
    cursor = db[1]
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user
# 로그인 확인 미들웨어
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

@app.get("/")
def read_root():
    return "StudyHero"
@app.post("/get_profile")
def get_profile(request: Request,refresh_token: Optional[str] = Cookie(None),access_token: Optional[str] = Cookie(None)):
    access_token = request.cookies.get("access_token")
    if access_token==None:
        raise HTTPException(status_code=404, detail="로그인 정보가 없습니다.")
    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        db = mysql_create_session()

        cursor = db[1]
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return user
    except jwt.JWTError:
        print("Token validation failed")
        raise HTTPException(status_code=401, detail="Token validation failed")
    except Exception as e:
        print(e)
        raise e
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
@app.get("/oauth/kakao")
async def oauth_kakao(code:str,response:Response):
    print(code)
    return code
@app.get("/oauth/kakao/callback")
def auth_kakao_callback(code: str,response: Response,request:Request):
    res = HTMLResponse("<body><script>window.close();</script></body>")
    token_response = requests.post(
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

    '''
        {
            'access_token': 64글자 문자열, 
            'token_type': 'bearer', 
            'refresh_token': 64글자 문자열, 
            'id_token': JWT 토큰 형식의 문자열, 
            'expires_in': Int, 
            'scope': 'profile_image talk_message profile_nickname friends', 
            'refresh_token_expires_in': Int
        }
        '''
    access_token = token_response_data.get("access_token")
    refresh_token = token_response_data.get("refresh_token")
    
    # get access token refresh
    # refresh_access_token(refresh_token)

    if access_token:
        user_response = requests.get(
                KAKAO_USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        user_data = user_response.json()
        # 얻을 수 있는 정보 : 고유ID, 유저 이름(닉네임), 프로필 이미지(원본),프로필 이미지(썸네일), 이메일
        """
        {
            'id': 0000000000, 
            'connected_at': '2021-12-13T14:55:37Z', 
            'properties': {
                'nickname': '김이현', 
                'profile_image': 'http://img1.kakaocdn.net/thumb/R640x640.q70/?fname=http://t1.kakaocdn.net/account_images/default_profile.jpeg', 
                'thumbnail_image': 'http://img1.kakaocdn.net/thumb/R110x110.q70/?fname=http://t1.kakaocdn.net/account_images/default_profile.jpeg'
            }, 
            'kakao_account': {
                'profile_nickname_needs_agreement': False, 
                'profile_image_needs_agreement': False, 
                'profile': {
                    'nickname': '김이현', 
                    'thumbnail_image_url': 'http://img1.kakaocdn.net/thumb/R110x110.q70/?fname=http://t1.kakaocdn.net/account_images/default_profile.jpeg', 
                    'profile_image_url': 'http://img1.kakaocdn.net/thumb/R640x640.q70/?fname=http://t1.kakaocdn.net/account_images/default_profile.jpeg', 
                    'is_default_image': True, 
                    'is_default_nickname': False
                }, 
                'has_email': True, 
                'email_needs_agreement': True
            }
        }


        {'id': 유저ID, 
        'connected_at': 시간(문자열), 
        'properties': 
            {
            'nickname': '유저명', 
            'profile_image': URL, 
            'thumbnail_image': URL
            }, 
        'kakao_account': 
            {
            'profile_nickname_needs_agreement': Boolean, 
            'profile_image_needs_agreement': Boolean, 
            'profile': 
                {
                'nickname': '유저명', 
                'thumbnail_image_url': URL,
                'profile_image_url': URL,
                'is_default_image': Boolean, 
                'is_default_nickname': Boolean
                }, 
            'has_email': Boolean, 
            'email_needs_agreement': Boolean
            }
        }
        """

        
        user_id = user_data.get("id")

        # 유저 폴더 생성
        if not os.path.exists(f"./static"):
            os.mkdir(f"./static")
        if not os.path.exists(f"./static/{user_id}"):
            os.mkdir(f"./static/{user_id}")
        if not os.path.exists(f"./static/{user_id}/profile_picture"):
            os.mkdir(f"./static/{user_id}/profile_picture")

        # 유저 프로필 다운로드(이미지, 썸네일)
        profile_image = user_data['properties']['profile_image']
        profile_image_path = f"./static/{user_id}/profile_picture/"+profile_image.split("/")[-1]
        profile_image_url = f"{BACK_URL}/static/{user_id}/profile_picture/"+profile_image.split("/")[-1]

        thumbnail_image = user_data['properties']['thumbnail_image']
        thumbnail_image_path = f"./static/{user_id}/profile_picture/thumbnail_"+thumbnail_image.split("/")[-1]

        profile_image_create_time = 0
        if not os.path.exists(profile_image_path):
            profile_req = requests.get(profile_image)
            if profile_req.status_code==200:
                profile_image_create_time = datetime.now()
                with open(profile_image_path,"wb+") as f:
                    f.write(profile_req.content)
        if not os.path.exists(thumbnail_image_path):
            thumbnail_req = requests.get(thumbnail_image)
            if thumbnail_req.status_code==200:
                profile_image_create_time = datetime.now()
                with open(thumbnail_image_path,"wb+") as f:
                    f.write(thumbnail_req.content)
        
        # 유저 데이터 받아오기
        user_nickname = user_data.get("kakao_account").get("profile").get("nickname")
        user_PI_argree = user_data.get("kakao_account").get("profile_nickname_needs_agreement")
        k_id = user_data.get("id")
        profile_image_id = random.randint(1,2**30) # 프로필 이미지 ID 임의로 발급
        user_create = datetime.now()
        user_update = datetime.now()
        user_age = 0

        k_id = random.randint(2**31,2**32) # 우리가 사용자에게 발급해주는 ID
        kakao_id = user_id # 카카오 API에서 주는 사용자의 ID값
        kakao_name = user_nickname # 카카오에 있는 유저명 가능? -> O
        kakao_tell = "01011111234" # 전화번호 수집 가능? -> X
        kakao_email = "" # 이메일 정보 가능 -> O
        kakao_birth = 0 # 생일정보 수집 가능? -> X
        kakao_refresh_token = token_response_data.get("refresh_token")
        kakao_access_token = token_response_data.get("access_token")


        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # DB에 사용자 정보 저장
        db = mysql_create_session()
        controller,cursor = db[0],db[1]
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            # kakao_api
            # k_id
            # kakao_id
            # kakao_name
            # kakao_tell
            # kakao_email
            # kakao_birth
            # kakao_create          option
            # kakao_update          option
            # kakao_image           option
            # kakao_refresh_token
            # kakao_access_token
        '''
                {
        'access_token': 64글자 문자열, 
        'token_type': 'bearer', 
        'refresh_token': 64글자 문자열, 
        'id_token': JWT 토큰 형식의 문자열, 
        'expires_in': Int, 
        'scope': 'profile_image talk_message profile_nickname friends', 
        'refresh_token_expires_in': Int
    }
        '''

        session_id = generate_session_id()
        session_data[session_id] = {"user_id":user_id,"create_at":time.time(),"expire":expire,"ip":request.client.host,"request":request,"sid":""}

        res.set_cookie(
            key="sessionid",
            value=session_id,
            httponly=True,  # JavaScript에서 접근 불가
            secure=True,    # HTTPS에서만 전송
            samesite="strict"  # 동일 사이트에서만 사용
        )

        user = cursor.fetchone()
        if not user:
            cursor.execute(
                "INSERT INTO proflie_image (pofile_image_id, profile_image_target, target_id, profile_image_url, profile_image_create) VALUES (%s, %s, %s, %s, %s)", 
                (profile_image_id,'user',k_id,profile_image_url,profile_image_create_time)
            )
            cursor.execute(
                "INSERT INTO kakao_api (k_id, kakao_id, kakao_name, kakao_tell, kakao_email, kakao_birth, kakao_refresh_token, kakao_access_token) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                (k_id,kakao_id,kakao_name,kakao_tell,kakao_email,kakao_birth,kakao_refresh_token,kakao_access_token)
            )
            cursor.execute(
                "INSERT INTO users (user_id, k_id, profile_image_id, user_nickname, user_xp, user_PI_argree, user_create, user_update, user_age) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                (user_id,k_id,profile_image_id,user_nickname,0,user_PI_argree, user_create,user_update,user_age)
            )
            controller.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user['user_id']
        
        return res
    return {"error": "인증 실패"}
@app.get('/get_userinfo')
async def get_userinformation(request:Request,current_user: dict =Depends(get_current_user)):
    return current_user
# 보호된 경로 : 미들웨어로 카카오 로그인 인증해야 접속 가능한 경로
@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"환영합니다, {current_user['user_nickname']}님!"}

# 테스트용
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
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ['BACKEND_PORT']),reload=True)