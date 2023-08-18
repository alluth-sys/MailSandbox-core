import os
import uuid
from datetime import datetime
from typing import Dict, List

import httpx
import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import t_pysql
from getmail import getMailProperty, getMessageValue, upLoadAttatchment

# import 區域
####################################################################################
# 建立fastAPI的東西

app = FastAPI()
HOST = "0.0.0.0"
PORT = 8777

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

# 建立fastAPI的東西
####################################################################################
# 定義 mail相關 route

# mail task的前端進入點
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

# 集大成mail的地方，包含上傳sql和minIO
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

# 看某一個mail task的status
@app.get("/taskStatus")
def taskStatus(taskID:str):
    isTaskDone(taskID)
    return t_pysql.getTaskStatus(taskID)

# 去看某個user的所有mail task
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
            "subjects":getSubjectsbyTaskID(task[1]),
            "isFinish":isTaskDone(task[1]),
            "createdTime":t_pysql.getTaskTIme(task[1])
        }
        result.append(dic)
    return result

# 依照某一個TaskID，取得所有mail subject
def getSubjectsbyTaskID(taskID):
    from t_pysql import getMailIDbyTaskID, getSubjectByMailID
    result = []
    mailIDs = getMailIDbyTaskID(taskID)
    for mailID in mailIDs:
        result.append(getSubjectByMailID(mailID))
    #print(result)
    return result

# 主要是會去看某一個mail task是否結束
def isTaskDone(taskID):
    rows = t_pysql.getTaskData(taskID)
    for row in rows:
        if row[2] == None:
            return False
    status = str(t_pysql.getTaskStatus(taskID)['status'])
    if status == "uploading_file_done":
        t_pysql.updateTaskStatus(taskID,"success")
        return True#True
    elif status == "success":
        return True
    return False

# 取得某一個mail task的結果，會把所有file根違反的東西列出來
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

# 用sql取得file違反的yara-rule
def getFileViolation(fileID:str):
    rows = t_pysql.getyaraResultByFileID(fileID)
    result = []
    for row in rows:
        result.append(row[1])
    return result


######################################################################################################################

######################################################################################################################

######################################################################################################################
# 定義 mail相關 route

# 動態分析相關status
# init
# finish_static_report
# start_generating_shot
# start_dynamic_analysis
# start_generating_aftershot
# start_processing_file
# generating_report
# report_upload_success

# 開始沙箱的地方
@app.post("/uploadDocument")
async def uploadDocument(file: UploadFile = File(...),taskID: str = Form(None), time: int = Form(None)):
    if not file:
        return {"error":"File not provided"}

    # 建立一個儲存檔案的地方
    #if not os.path.exists("files"):
    #    os.makedirs(files)

    # 把東西儲存進去
    #file_path = 'C:\\Users\\wxkang\\Desktop\\uploadFile\\raw\\' + file.filename
    #with open(file_path, "wb+") as file_object:
    #    file_object.write(await file.read())

    if taskID is None:
        taskID = str(uuid.uuid4())
    if time is None:
        time = 10
    
    # 建立新的Task
    newtask = DTask()
    newtask.filename = file.filename
    newtask.createTime = datetime.now()
    newtask.status = "init"
    taskList[taskID] = newtask

    # 把檔案request進去
    url = "http://host.docker.internal:8000/startSand/"
    data = {'taskID': taskID,'time':time}
    await requestFile(url,data,file)
    #return {"filename":file.filename}
    return {"taskID":taskID}

class Status(BaseModel):
    taskID: str
    status: str

class DTask():
    filename: str
    status: str         
    # init,start static analysis, start generating shot, start dynamic analysis
    # start generating aftershot, start processing file, generating report, done
    createTime: str

taskList: Dict[str, DTask] = {}

# 主要是內部給外部的東西
@app.post("/uploadfiles")
async def create_upload_file(file: UploadFile = File(...),perpose:str = Form(None),taskID:str = Form(None)):
    #先在data底下建立task資料夾
    # 建立一個名為 'my_folder' 的資料夾
    taskdata_path = './data/' + str(taskID)
    if not os.path.exists(taskdata_path):
        os.mkdir(taskdata_path)
    #確定是哪一類檔案，儲存zip到指定資料夾
    if perpose == "static":
        file_location = taskdata_path + "/static.zip"
    if perpose == "dynamic":
        file_location = taskdata_path + "/dynamic.zip"
    #儲存檔案
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    if perpose == "dynamic":
        outputfiles = ["pdfparser.txt",\
               "trid.txt",\
            "hkcr_differences.txt",\
            "hkcu_differences.txt",\
            "hklm_differences.txt",\
            "hku_differences.txt",\
            "hkcc_differences.txt",\
            #"Logfile.csv",\
            "1_init.jpg",\
            "2_procmon.jpg",\
            "3_openFile.jpg",\
            "4_closeFile.jpg"]
        unzip_upload_gcp(outputfiles=outputfiles,taskID=taskID)
        taskList[taskID].status = "report_upload_success"

    #解壓縮
    return {"info": f"file '{file.filename}' saved at location: {file_location}"}

# 這邊是去更新task list裡面的task
@app.post("/updateStatus")
async def updateStatus(status:str = Form(None),taskID:str = Form(None)):
    taskList[taskID].status = status
    return "updata Success"

@app.get("/testGOGO/")
async def testGOGO():
    return getSubjectsbyTaskID("dododo888")

@app.get("/getTaskStatus")
async def getTaskStatus():
    result = []
    for i in taskList:
        newlist = {}
        newlist["id"] = i
        print(taskList[i])
        newlist["filename"] = taskList[i].filename
        newlist["createTime"] = taskList[i].createTime
        newlist["status"] = taskList[i].status
        result.append(newlist)
    return result

async def requestFile(url,data,file):
    # 把檔案request進去
    #url = "http://192.168.245.128:8000/uploadfiles/"
    #data = {'taskID': taskID,'time':time}
    file_content = await file.read()
    files = {"file": (file.filename, file_content, file.content_type)}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, files=files,data=data)
    print("this is request site", response)
    return 'good'


def unzip_upload_gcp(outputfiles,taskID):
    import zipfile
    zip_path = 'data/' + taskID + "/" + "static.zip"
    extract_path = 'data/'+taskID
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    zip_path = 'data/' + taskID + "/" + "dynamic.zip"
    extract_path = 'data/'+taskID
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    upLoadToGCP(taskID,outputfiles)

def upLoadToGCP(taskID,outputfiles):
    import os

    from google.cloud import storage
    GCP_BUCKET_NAME = "kowala-result"
    GCP_CREDENTIALS_FILE = "kowala-396107-cd92e9e2bf76.json"  # your GCP service account JSON key
    storage_client = storage.Client.from_service_account_json(GCP_CREDENTIALS_FILE)
    bucket = storage_client.get_bucket(GCP_BUCKET_NAME)
    for filename in outputfiles:
        local_path = "./data/" + taskID + "/" + filename
        #blob_name = os.path.basename(local_path)
        blob = bucket.blob(taskID+'_'+filename)
        with open(local_path,'rb') as f:
            print("Uploading:"+filename)
            blob.upload_from_file(f)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)



# 以前的登入Azure區域，捨不得刪除 : )

# from starlette.status import HTTP_401_UNAUTHORIZED
# import msal

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