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
from db_util import message_image,message_read,message_text,message_video,message_voice,message_table
from db_util import planner
from db_util import profile_image
from db_util import room_users
from db_util import user_table

from db_util.models import *

import sys
import base64
from starlette.staticfiles import StaticFiles
import logging

logging.getLogger("sqlalchemy.engine").disabled = True


BACK_URL = "https://api.studyhero.kr"
FRONT_URL = "https://studyhero.kr"


KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


KAKAO_REDIRECT_URI = os.environ['KAKAO_REDIRECT_URI']
KAKAO_CLIENT_ID = os.environ['KAKAO_CLIENT_ID']
KAKAO_CLIENT_SECRET = os.environ['KAKAO_CLIENT_SECRET']
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


os.environ['BACKEND_PORT']='8090'

KAKAO_REDIRECT_URI = os.environ['KAKAO_REDIRECT_URI']
KAKAO_CLIENT_ID = os.environ['KAKAO_CLIENT_ID']
KAKAO_CLIENT_SECRET = os.environ['KAKAO_CLIENT_SECRET']


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

session_data = {}
socket_session_data = {}
SWAGGER_HEADERS = {
    "title": "SWAGGER UI 변경 테스트",
    "version": "1.0.1",
    "description": "StudyHero API Swagger입니다",
    "contact": {
        "name": "Ehyun",
        "url": "https://studyhero.kr",
        "email": "lh7721004@naver.com",
        "license_info": {
        
        },
    },
}


# 유저 프로필 가져오는 로직에 mbti, 나이, 등 가져오기, 프로필 편집 페이지에 있는 정보들 가져오게 하기
async def get_current_user(request: Request,response_model=User):
    sessionid = request.cookies.get("sessionid")
    if sessionid==None or not sessionid in session_data.keys():
        raise HTTPException(status_code=404, detail="로그인 정보가 없습니다.")
    user_id = session_data[sessionid]['user_id']
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    if session_data[sessionid]["expire"]<time.time():
        user = kakao_api.get_kakao_api_by_user_id(user_id)
        access_token = user.kakao_access_token
        user_response = requests.get(
                KAKAO_USER_INFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if user_response.status_code//100<4:
            session_data[sessionid]["expire"] = (datetime.now(timezone(timedelta(hours=9))) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
        else:
            # 액세스 토큰 만료
            refresh_token = user.kakao_refresh_token
            grant_type = "refresh_token"
            header = {"Content-type": "application/x-www-form-urlencoded;charset=utf-8"}
            data={
                        "grant_type": grant_type,
                        "client_id": KAKAO_CLIENT_ID,
                        "refresh_token": refresh_token,
                        "client_secret": KAKAO_CLIENT_SECRET,
                    }
            # 토큰 갱신
            res = requests.post("https://kauth.kakao.com/oauth/token",headers=header,data=data)
            if res.status_code//100<4:
                result = kakao_api.update_kakao_api(user.k_id,{"kakao_access_token":res["access_token"],"kakao_refresh_token":res["kakao_refresh_token"]})
            else:
                raise HTTPException(status_code=res.status_code, detail="Something Wrong While refreshing access token")

    return user_table.get_user_with_profile_image(user_id)
    
def generate_session_id():
    return str(uuid4())

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
@app.get("/cookie")
def test_get(request:Request):
    return str(request.cookies)
@app.post("/test")
def test_root():
    return [{"sender":"12","messge":"hello","time":10,"image":"image"},{"sender":"12","messge":"hello","time":10,"image":"image"},{"sender":"12","messge":"hello","time":10,"image":"https://s.pstatic.net/dthumb.phinf/?src=%22https%3A%2F%2Fs.pstatic.net%2Fmimgnews%2Fimage%2Forigin%2F665%2F2024%2F11%2F05%2F3942.jpg%3Fut%3D20241105174614%22&type=nf312_208&service=navermain"}]
@app.post("/logout")
async def test_logout(request:Request,current_user:dict=Depends(get_current_user)):
    # "sessionid" 쿠키 읽기
    if 'sessionid' in request.cookies.keys():
        sessionid = request.cookies.get("sessionid")
        if not sessionid:
            return JSONResponse(content={"msg": "No active session found"}, status_code=400)
        
        # 세션 데이터 제거
        if sessionid in session_data:
            socketid = session_data[sessionid]["sid"]
            if socketid in socket_session_data:
                del socket_session_data[socketid]
            del session_data[sessionid]
        
        
        return JSONResponse(content={"msg": "logout successfully"}, status_code=200)
    return JSONResponse(content={"msg": "logout fail"}, status_code=400)

# 카카오 OAuth 키 값 자리
@app.get("/auth/kakao")
async def auth_kakao():
    return RedirectResponse(
        url=f"{KAKAO_AUTH_URL}?client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code"
    )
@app.get("/oauth/kakao/callback")
def auth_kakao_callback(code: str,response: Response,request:Request):
    try:
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

        access_token = token_response_data.get("access_token")
        refresh_token = token_response_data.get("refresh_token")
        
        if access_token:
            user_response = requests.get(
                    KAKAO_USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
            user_data = user_response.json()        
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
            user_PI_agree = user_data.get("kakao_account").get("profile_nickname_needs_agreement")
            k_id = user_data.get("id")
            profile_image_id = random.randint(1,2**30) # 프로필 이미지 ID 임의로 발급
            user_create = datetime.now()
            user_update = datetime.now()
            user_age = 0

            k_id = random.randint(2**31,2**32) # 우리가 사용자에게 발급해주는 ID
            kakao_id = user_id # 카카오 API에서 주는 사용자의 ID값
            kakao_name = user_nickname # 카카오에 있는 유저명 가능? -> O
            kakao_tel = "01011111234" # 전화번호 수집 가능? -> X
            kakao_email = "" # 이메일 정보 가능 -> O
            kakao_birth = 0 # 생일정보 수집 가능? -> X
            kakao_refresh_token = token_response_data.get("refresh_token")
            kakao_access_token = token_response_data.get("access_token")

            expire = (datetime.now(timezone(timedelta(hours=9))) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()

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
                kakao_api.create_kakao_api(
                    k_id=k_id,
                    kakao_id=kakao_id,
                    kakao_name=kakao_name,
                    kakao_tel=kakao_tel,
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
                    user_PI_agree=user_PI_agree,
                    user_age=user_age,
                    user_mbti=None,
                    user_job=None,
                    user_study_field=None)
                    
            
            return res
    except Exception as e:
        return {"error": "인증 실패","Exception":str(e)}
        
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
            return JSONResponse(content={"msg":"update fail"},status_code=400)
        else:
            return JSONResponse(content={"msg":"updated successfully"},status_code=200)
    except Exception as e:
        return Response(content=str(e),status_code=400)

@app.post("/profile/delete")
def delete_profile(request:Request,current_user:dict=Depends(get_current_user)):
    if user_table.delete_user(current_user['user']['user_id']):
        return Response(content="Successfully Delete your account",status_code=200)
    else:
        return Response(content="Failed Delete your account",status_code=400)

@app.post("/ranking/get")
def get_ranking(request:Request,current_user:dict=Depends(get_current_user)):
    return chatting_room.get_top_chatrooms()

@app.post("/chatroom/create")
async def create_chatroom(request:Request,current_user:dict=Depends(get_current_user)):

    req_data = await request.json()
    hashtag_data = req_data['hashtag']
    hashtag_id = random.randint(0,2**30)
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
    for i in hashtag_data.split():
        hashtag.create_hashtag(hashtag_id,room_id,i)
        hashtag_id = random.randint(0,2**30)

    room_users.create_room_user(room_id=room_id,user_id=current_user['user']['user_id'])
    
    return JSONResponse(content={"room_id":room_id},status_code=200)
@app.post("/chat/get")
async def get_all_chats(request:Request,current_user:dict=Depends(get_current_user)):
    request_data = await request.json()
    room_code = int(request_data['room_id'])
    return room_users.test(room_code)
@app.post("/chatroom/update")
def update_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
    pass
@app.post("/chatroom/get")
async def get_chatroom(request:Request,current_user:dict=Depends(get_current_user),response_model=RoomUser):
    request_data = await request.json()
    return room_users.get_room_by_room_id(request_data['room_id'])
@app.post("/chatroom/get/all")
async def get_all_chatroom(request:Request,current_user:dict=Depends(get_current_user),response_model=RoomUser):
    return room_users.get_rooms_for_user_with_hashtags(current_user['user']['user_id'])
@app.post("/chatroom/join")
async def join_chatroom(request:Request,current_user:dict=Depends(get_current_user)):
    request_data = await request.form()
    room_code = int(request_data['room_code'])
    room_users.create_room_user(room_code,current_user['user']['user_id'])
    return Response(content="ChatRoom Created Successfully",status_code=201)

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


# 캘린더, 플래너 crud
@app.post("/studyplanner/get")
async def get_studyplanner(request:Request,current_user:dict=Depends(get_current_user)):
    user_id = current_user['user_id']
    request_data = await request.json()
    planner_id = request_data['planner_id']

    return planner.get_planner_by_id(planner_id=planner_id)
@app.post("/studyplanner/search")
async def get_studyplanner(request:Request,current_user:dict=Depends(get_current_user)):
    request_data = await request.json()
    request_data['year'] = request_data['year'].replace("년","")
    request_data['month'] = request_data['month'].replace("월","")
    request_data['day'] = request_data['day'].replace("일","")
    result = planner.get_planner_by_date(year=int(request_data['year']),
    month=int(request_data['month']),
    day=int(request_data['day']))
    return result
# 캘린더, 플래너 crud
@app.post("/studyplanner/create")
async def create_studyplanner(request:Request,current_user:dict=Depends(get_current_user)):
    try:
        user_id = current_user['user']['user_id']
        request_data = await request.json()

        request_data['planner_year'] = request_data['planner_year'].replace("년","")
        request_data['planner_month'] = request_data['planner_month'].replace("월","")
        request_data['planner_date'] = request_data['planner_date'].replace("일","")

        request_data['planner_year'] = (4-len(request_data['planner_year']))*"0"+request_data['planner_year']
        request_data['planner_month'] = (2-len(request_data['planner_month']))*"0"+request_data['planner_month']
        request_data['planner_date'] = (2-len(request_data['planner_date']))*"0"+request_data['planner_date']
        
        planner_id = random.randint(0,2**30)
        
        planner_date = datetime.strptime(str(request_data['planner_year'])+"-"+str(request_data['planner_month'])+"-"+str(request_data['planner_date']), '%Y-%m-%d')
        
        
        planner_schedule_name = request_data['planner_schedule_name']
        planner_schedule_status = request_data['planner_schedule_status']
        planner.create_planner(planner_id=planner_id,user_id=user_id,planner_date=planner_date,planner_schedule_name=planner_schedule_name,planner_schedule_status=planner_schedule_status)
        return Response(content="Studyplanner Created Successfully",status_code=201)
    except Exception as e:
        return Response(content="Studyplanner Create Something Wrong",status_code=417)
@app.post("/studyplanner/update")
async def update_studyplanner(request:Request,current_user: dict=Depends(get_current_user)):
    try:
        request_data = await request.json()
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

@app.post("/calender/getall")
async def get_calender(request:Request,current_user: dict =Depends(get_current_user)):
    try:
        response = calender.get_all_calendars_by_user_id(current_user['user']['user_id'])
        res = []
        for cal in response:
            is_dday = True
            if cal.calender_is_dday==0:
                is_dday = False
            res.append({
                    "id":cal.calender_id,
                    "date":cal.calender_date_start,
                    "title":cal.calender_schedule_name,
                    "memo":cal.calender_schedule_memo,
                    "isDDay":is_dday
                })
        return res
    except:
        return Response(content="Cant not found Calender",status_code=404)
@app.post("/calender/get")
async def get_calender(request:Request,current_user: dict =Depends(get_current_user)):
    try:
        request_data = await request.form()
        start_date = request_data['start_date']
        finish_date = request_data['finish_date']
        calender.get_calender_in_date(start_date=start_date,finish_date=finish_date)
        return Response(content="Calender Deleted Successfully",status_code=200)
    except:
        return Response(content="Cant not found Calender",status_code=404)
@app.post("/calender/create")
async def create_calender(request:Request,current_user: dict =Depends(get_current_user)):
    try:
        request_data = await request.json()
        calender_id = random.randint(0,2**30)
        start_date = request_data['date'].split("T")[0]
        finish_date = request_data['date'].split("T")[0]
        isdday = request_data['isdday']
        name = request_data['title']
        memo = request_data['memo']
        calender.create_calendar(
            user_id=current_user['user']['user_id'],
            calender_id=calender_id,
            start_date=start_date,
            finish_date=finish_date,
            name=name,
            memo=memo,
            isdday=isdday)
        return Response(content="Calender Created Successfully",status_code=200)
    except Exception as e:
        return Response(content="Calender Create Something Wrong",status_code=417)
@app.post("/calender/update")
async def update_calender(request:Request,current_user: dict =Depends(get_current_user)):
    try:
        request_data = await request.json()
        calender_id = request_data['id']
        start_date = request_data['date'].split("T")[0]
        finish_date = request_data['date'].split("T")[0]
        isdday = 0
        if request_data['isdday']:
            isdday = 1
        name = request_data['title']
        memo = request_data['memo']
        calender.update_calendar(calender_id=calender_id,start_date=start_date,finish_date=finish_date,name=name,memo=memo,isdday=isdday)
        return Response(content="Calender Updated Successfully",status_code=200)
    except Exception as e:
        return Response(content="Calender Delete Something Wrong",status_code=417)
@app.post("/calender/delete")
async def delete_calender(request:Request,current_user: dict =Depends(get_current_user)):
    try:
        request_data = await request.json()
        calender_id = request_data['calender_id']
        calender.delete_calendar(calender_id=calender_id)
        return Response(content="Calender Deleted Successfully",status_code=200)
    except:
        return Response(content="Calender Delete Something Wrong",status_code=417)



sio = socketio.AsyncServer(async_mode='asgi',cors_allowed_origins=origins) #socketio 서버 생성
app = socketio.ASGIApp(sio, app) #메인 서버와 socketio서버 통합

@sio.on('message')
async def send_message(sid, data):
    room = data.get("room_code")
    message = data.get("message")

    file_name = data.get("fileName")
    file_data = data.get("filedata")

    sessionid = socket_session_data[sid]['sessionid']
    if (not sessionid) or (not (sessionid in session_data.keys())) or (session_data[sessionid]['expire']<time.time()):
        await sio.emit("redirect", {"url": "/login"}, room=room)
        return
    user_id = get_user_by_sessionid(sessionid).user_id
    user_table.increase_user_xp(user_id)
    message_id = random.randint(2,2**30)
    text_id = random.randint(2,2**30)
    message_table.create_message(message_id,user_id,room,"text")
    message_text.create_message_text(text_id,message_id,message)
    
    file_path = None
    if file_name and file_data:
        UPLOAD_DIR = "./static/chat/"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(bytearray(file_data))
    data = data["user"]
    await sio.emit("receive_message",{
        "profile_image":{
            "profile_image_id":data["profile_image"]["profile_image_id"],
            "profile_image_target":data["profile_image"]["profile_image_target"],
            "target_id":data["profile_image"]["target_id"],
            "profile_image_url":data["profile_image"]["profile_image_url"],
            "profile_image_create":str(data["profile_image"]["profile_image_create"])},
        "user":{
            "user_id":data["user"]["user_id"],
            "k_id":data["user"]["k_id"],
            "profile_image_id":data["user"]["profile_image_id"],
            "user_nickname":data["user"]["user_nickname"],
            "user_xp":data["user"]["user_xp"],
            "user_PI_agree":data["user"]["user_PI_agree"],
            "user_create":str(data["user"]["user_create"]),
            "user_update":str(data["user"]["user_update"]),
            "user_age":data["user"]["user_age"],
            "user_mbti":data["user"]["user_mbti"],
            "user_job":data["user"]["user_job"],
            "user_study_field":data["user"]["user_study_field"]},
        "message": message,"sessionid":sessionid,"file":file_path}, room=room)
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
        user = get_user_by_sessionid(sessionid)
        if cookies and sessionid:
            if room:  # room 정보가 있으면 클라이언트를 해당 room에 참여시킴
                await sio.enter_room(sid, room)
                await sio.emit("connect_success", data={"user": {
                    'k_id':user.k_id, 'profile_image_id':user.profile_image_id, 'user_nickname':user.user_nickname, 'user_xp':user.user_xp, 
                    'user_PI_agree':user.user_PI_agree, 'user_age':user.user_age, 'user_mbti':user.user_mbti, 'user_job':user.user_job, 
                    'user_study_field':user.user_study_field}, "message": f"Connected to room {room}!", "sessionid": sessionid}, room=sid)
            else: # room 정보가 없는 곳 접속
                await sio.emit("redirect", {"url": "/"}, room=room)
        else:
            await sio.disconnect(sid)
    except Exception as e:
        await sio.emit(event="redirect",data= {"url": "/login"}, to=sid)
@sio.event
async def disconnect(sid):
    if sid in socket_session_data.keys():
        del socket_session_data[sid]
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ['BACKEND_PORT']))
