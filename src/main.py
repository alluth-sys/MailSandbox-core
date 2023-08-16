import os
from typing import List

import msal
import uvicorn
from fastapi import (BackgroundTasks, FastAPI, File, HTTPException, Request,
                     UploadFile)
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED

import t_pysql
from getmail import getMailProperty, getMessageValue, upLoadAttatchment
from t_yamlReader import getyamlkey

app = FastAPI()
HOST = "0.0.0.0"
PORT = 8777

# 以前的登入Azure區域

# @app.get("/login")
# def login(request: Request):
#     # 初始化 MSAL
#     config = {
#         "client_id": getyamlkey('graph_client'),  # 從環境變數取得 client_id
#         "authority": "https://login.microsoftonline.com/common",
#         "redirect_uri": "http://localhost:8777/callback",  # 將回調地址改為你 FastAPI 服務的一個路由
#         "scope": ["https://graph.microsoft.com/.default"],
#     }

#     app = msal.PublicClientApplication(config['client_id'], authority=config['authority'])

#     # 建立登入的 URL 並重定向用戶到該 URL
#     auth_url = app.get_authorization_request_url(config['scope'], redirect_uri=config['redirect_uri'])
#     return RedirectResponse(auth_url)

# @app.get("/callback")
# def callback(code: str):
#     # 初始化 MSAL
#     config = {
#         "client_id": getyamlkey('graph_client'),
#         "authority": "https://login.microsoftonline.com/common",
#         "redirect_uri": "http://localhost:8777/callback",
#         "scope": ["https://graph.microsoft.com/.default"],
#     }

#     app = msal.PublicClientApplication(config['client_id'], authority=config['authority'])

#     # 使用授權碼獲取 token
#     result = app.acquire_token_by_authorization_code(code, config['scope'], redirect_uri=config['redirect_uri'])
    
#     if "access_token" in result:
#         # 成功取得 token，返回結果（或進行其他處理）
#         access_token = result['access_token']
        

#         # TODO: 之後這邊應該會回傳到某一個地方
#         return access_token
#     else:
#         # 取得 token 失敗，返回錯誤信息
#         return HTTPException(
#             status_code=HTTP_401_UNAUTHORIZED,
#             detail=result.get('error_description', 'Unknown error'),
#         )

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立一個basemodel
class Task(BaseModel):
    taskID: str
    token: str
    userID: str
    message_list: List[str]

@app.post("/task")
async def create_task(task: Task,background_task:BackgroundTasks,getMailProperty=getMailProperty,getMessageValue=getMessageValue):
    """give sufficient information and it will upload specific attatchment to minIO

    Args:
        task (Task): contain taskID(str), token(str) and message_list(List[str])

    Returns:
        str: task id
    """
    background_task.add_task(creatingtask,task)
    return {"taskID": task.taskID}

def creatingtask(task: Task,getMailProperty=getMailProperty,getMessageValue=getMessageValue):
    print("starting creating task")
    t_pysql.insert_userTask(userID=task.userID,taskID=task.taskID)
    t_pysql.insert_task(taskID=task.taskID)
    t_pysql.updateTaskStatus(task.taskID,"initializing")

    for message in task.message_list:
        try:
            mail = getMessageValue(token=task.token,messageID=message)
            MessageID, Subject, Received, Sender= getMailProperty(mail)
        except ValueError as err:
            t_pysql.updateTaskStatus(task.taskID,"graph_api_token_failed")
            t_pysql.insert_taskError(taskID=task.taskID,error="Error:Graph_API_Token_Faile")
            print(err)
            return "Error"
        #把id抓下來跟資料庫比對
        if not t_pysql.check_duplicate_id(message):
            print("check mid duplicate")
            t_pysql.insert_maildata(MessageID, Subject, Received,Sender)
            # 假如id不在，把property加上去資料庫
        # 把messageID跟taskID一起放進資料庫
        print("start upload")
        t_pysql.updateTaskStatus(task.taskID,"start_uploading_file")
        uploadResult = upLoadAttatchment(token=task.token,taskID=task.taskID,messageID=message)
        if uploadResult[0:5] == "Error":
            t_pysql.insert_taskError(taskID=task.taskID,error=uploadResult)
            t_pysql.updateTaskStatus(task.taskID,uploadResult)
            return "error"
        t_pysql.insert_messageTask(message,task.taskID)
    t_pysql.updateTaskStatus(task.taskID,"uploading_file_done")
    

@app.get("/taskStatus")
def taskStatus(taskID:str):
    isTaskDone(taskID)
    return t_pysql.getTaskStatus(taskID)

@app.get("/checkTask")
def checkTask(userID:str):
    """check wheather the task is done, it check the column isbad == None in database

    Args:
        taskID (str): the task id specific on front-end

    """
    userTasks = t_pysql.getTaskByUser(userID)
    result = []
    for task in userTasks:
        dic = {
            "taskID":task[1],
            "isFinish":isTaskDone(task[1])
        }
        result.append(dic)
    return result

def isTaskDone(taskID):
    rows = t_pysql.getTaskData(taskID)
    for row in rows:
        if row[2] == None:
            return False
    status = str(t_pysql.getTaskStatus(taskID)["status"])
    if status == "uploading_file_done":
        t_pysql.updateTaskStatus(taskID,"success")
        return True#True
    elif status == "success":
        return True
    return False

@app.get("/showResult")
def showResult(taskID:str):
    files = t_pysql.getFileIDByTask(taskID)
    result = []
    for file in files:
        dic = {
            "filename":file[1],
            "violations":getFileViolation(file[0])
        }
        result.append(dic)

    #rows = t_pysql.getyaraResult(taskID)
    return result

def getFileViolation(fileID:str):
    rows = t_pysql.getyaraResultByFileID(fileID)
    result = []
    for row in rows:
        result.append(row[1])
    return result

@app.post("/uploadDocument")
async def uploadDocument(file: UploadFile = None):
    if not file:
        return {"error": "File not provided"}
    
    if not os.path.exists('files'):
        os.makedirs('files')

    file_location = os.path.join('files', file.filename)
    
    with open(file_location, "wb") as buffer:
        buffer.write(file.file.read())
    return {"filename": file.filename}

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)