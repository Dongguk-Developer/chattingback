from fastapi.middleware.cors import CORSMiddleware
import os
import socketio
from fastapi.responses import RedirectResponse,HTMLResponse,JSONResponse
import requests
from datetime import datetime, timedelta,timezone
from datetime import date
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

from db_util.models import *

import sys
import base64
from starlette.staticfiles import StaticFiles


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

# print(chatting_room.get_top_chatrooms())

# 유저 프로필 가져오는 로직에 mbti, 나이, 등 가져오기, 프로필 편집 페이지에 있는 정보들 가져오게 하기
async def get_current_user(request: Request,response_model=User):
    return user_table.get_user_with_profile_image(2032376189)
    sessionid = request.cookies.get("sessionid")
    print(session_data[sessionid])
    user_id = session_data[sessionid]['user_id']
    if sessionid==None or not sessionid in session_data.keys():
        raise HTTPException(status_code=404, detail="로그인 정보가 없습니다.")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    print(kakao_api.get_kakao_api_by_user_id(user_id))
    print(session_data[sessionid]["expire"])
    if session_data[sessionid]["expire"]<time.time():
        print(kakao_api.get_kakao_api_by_user_id(user_id))


    
    return user_table.get_user_with_profile_image(user_id)

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
if DEV_MODE:
    origins.append("http://localhost")
    origins.append("http://localhost:3000")
    origins.append("http://localhost:3001")
    origins.append("http://localhost:3002")
    origins.append("http://localhost:3003")
    origins.append("http://localhost:8090")
    origins.append("null")
    origins.append(None)
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
app.mount("/static", StaticFiles(directory="static"), name="static")

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
@app.get("/test")
def test_get():
    return "testget"
@app.post("/test")
def test_root():
    return [{"sender":"12","messge":"hello","time":10,"image":"image"},{"sender":"12","messge":"hello","time":10,"image":"image"},{"sender":"12","messge":"hello","time":10,"image":"https://s.pstatic.net/dthumb.phinf/?src=%22https%3A%2F%2Fs.pstatic.net%2Fmimgnews%2Fimage%2Forigin%2F665%2F2024%2F11%2F05%2F3942.jpg%3Fut%3D20241105174614%22&type=nf312_208&service=navermain"}]

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
        origin_profile_image_url = user_data['properties']['profile_image']
        profile_image_path = f"./static/{user_id}/profile_picture/"+origin_profile_image_url.split("/")[-1]
        profile_image_url = f"{BACK_URL}/static/{user_id}/profile_picture/"+origin_profile_image_url.split("/")[-1]

        thumbnail_image = user_data['properties']['thumbnail_image']
        thumbnail_image_path = f"./static/{user_id}/profile_picture/thumbnail_"+thumbnail_image.split("/")[-1]

        profile_image_create_time = 0
        if not os.path.exists(profile_image_path):
            profile_req = requests.get(origin_profile_image_url)
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

        expire = (datetime.now(timezone(timedelta(hours=9))) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
        
        print(384,expire)
        # DB에 사용자 정보 저장
        # db = mysql_create_session()
        # controller,cursor = db[0],db[1]
        # cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
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

        user = user_table.get_user_by_id(user_id)
        if not user:

            profile_image.create_profile_image(profile_image_id,'user',k_id,profile_image_url,profile_image_create_time)
            # cursor.execute(
            #     "INSERT INTO proflie_image (pofile_image_id, profile_image_target, target_id, profile_image_url, profile_image_create) VALUES (%s, %s, %s, %s, %s)", 
            #     (profile_image_id,'user',k_id,profile_image_url,profile_image_create_time)
            # )
            kakao_api.create_kakao_api(
                k_id=k_id,
                kakao_id=kakao_id,
                kakao_name=kakao_name,
                kakao_tell=kakao_tell,
                kakao_email=kakao_email,
                kakao_birth=kakao_birth,
                kakao_create=datetime.utcnow(),
                kakao_update=datetime.utcnow(),
                kakao_image=origin_profile_image_url,
                kakao_refresh_token=kakao_refresh_token,
                kakao_access_token=kakao_access_token)
            user_table.create_user(
                user_id=user_id,
                k_id=k_id,
                profile_image_id=profile_image_id,
                user_nickname=user_nickname,
                user_xp=0,
                user_PI_argree=user_PI_argree,
                user_age=user_age,
                user_mbti=None,
                user_job=None,
                user_study_field=None)
                
        
        return res
    return {"error": "인증 실패"}
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
        user_id = current_user['user']['user_id']
        request_data = await request.json()
        mbti = None
        name = None
        age = None
        job = None
        studyfield = None
        xp = None
        profile_image_path = None
        filename = None
        if 'mbti' in request_data.keys():
            mbti = request_data['mbti']
        if 'name' in request_data.keys():
            name = request_data['name']
        if 'age' in request_data.keys():
            age = request_data['age']
        if 'job' in request_data.keys():
            job = request_data['job']
        if 'studyfield' in request_data.keys():
            studyfield = request_data['studyfield']
        if 'xp' in request_data.keys():
            xp = request_data['xp']
        if 'profile_image' in request_data.keys() and request_data['profile_image']:
            data = request_data['profile_image']
            if data.startswith("http"):
                file = None
            else:
                base64_data = data.split(",")[1]
                ext = data.split(",")[0].split("/")[1].split(";")[0]
                image_data = base64.b64decode(base64_data)
                if not os.path.exists("./static"):
                    os.mkdir("./static")
                if not os.path.exists(f"./static/{user_id}"):
                    os.mkdir(f"./static/{user_id}")
                if not os.path.exists(f"./static/{user_id}/profile_picture/"):
                    os.mkdir(f"./static/{user_id}/profile_picture/")
                filename = str(int(time.time()))+"."+ext
                profile_image_path = f"./static/{user_id}/profile_picture/"+filename
                with open(profile_image_path, "wb+") as file:
                    file.write(image_data)
        else:
            file = None
        if profile_image_path!=None:
            new_profile_image_id = random.randint(0,2**30)
            new_profile_image_target = "user"
            new_target_id = user_id
            new_profile_image_url = BACK_URL+profile_image_path[1:]
            new_profile_image_create = datetime.now()
            profile_image.create_profile_image(
                profile_image_id=new_profile_image_id,
                profile_image_target=new_profile_image_target, 
                target_id=new_target_id, 
                profile_image_url=new_profile_image_url, 
                profile_image_create=new_profile_image_create)

            update_result = user_table.update_user(user_id=user_id,user_nickname=name,user_xp=xp,user_age=age,user_mbti=mbti,user_job=job,user_study_field=studyfield,profile_image_id=new_profile_image_id)
        else:
            update_result = user_table.update_user(user_id=user_id,user_nickname=name,user_xp=xp,user_age=age,user_mbti=mbti,user_job=job,user_study_field=studyfield)
        if update_result==None:
            return JSONResponse(content={"msg":"update fail 256"},status_code=400)
        else:
            return JSONResponse(content={"msg":"updated successfully"},status_code=200)
    except Exception as e:
        print("Excption!!",e)
        return Response(content=str(e),status_code=400)


@app.post("/ranking/get")
def get_ranking(request:Request,current_user:dict=Depends(get_current_user)):
    pass

@app.post("/chatroom/create")
async def create_chatroom(request:Request,current_user:dict=Depends(get_current_user)):

    req_data = await request.json()
    room_id = random.randint(0,2**30)
    new_profile_image_id = random.randint(0,2**30)
    new_profile_image_target = "chattingroom"
    new_target_id = room_id
    new_profile_image_url = BACK_URL+'/static/chatroom/default/default.png'
    new_profile_image_create = datetime.now()

    profile_image.create_profile_image(
        profile_image_id=new_profile_image_id,
        profile_image_target=new_profile_image_target, 
        target_id=new_target_id, 
        profile_image_url=new_profile_image_url, 
        profile_image_create=new_profile_image_create)
    
    chatting_room.create_chatting_room(
        room_id=room_id,
        profile_image_id=new_profile_image_id,
        room_type='',
        room_name=req_data['title'],
        room_manager=current_user['user']['user_id'],
        room_total_users=1
    )
    room_users.create_room_user(room_id=room_id,user_id=current_user['user']['user_id'])
    
    pass
@app.post("/chatroom/update")
def update_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
    pass
@app.post("/chatroom/get")
async def get_chatroom(request:Request,current_user:dict=Depends(get_current_user),response_model=RoomUser):
    # return "get"
    print(580,room_users.get_rooms_for_user(current_user['user']['user_id']))
    return room_users.get_rooms_for_user(current_user['user']['user_id'])
# @app.post("/chatroom/get")
# def delete_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
#     pass
@app.post("/chatroom/join")
async def join_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
    # try:
    request_data = await request.form()
    room_code = int(request_data['room_code'])
    print(current_user)
    room_users.create_room_user(room_code,current_user['user']['user_id'])
    return Response(content="ChatRoom Created Successfully",status_code=201)
    # except Exception as e:
    #     print(562,e)
    #     return Response(content="ChatRoom Create Something Wrong",status_code=417)

    
@app.post("/chatroom/out")
async def out_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
    try:
        request_data = await request.json()
        room_code = None
        if 'room_code' in request_data.keys():
            room_code = request_data['room_code']
        room_users.delete_room_user(room_code,current_user['user_id'])
        return Response(content="ChatRoom Exit Successfully",status_code=200)
    except:
        return Response(content="ChatRoom Exit Something Wrong",status_code=417)


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