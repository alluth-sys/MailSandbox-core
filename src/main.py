from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from t_yamlReader import getyamlkey
import t_pysql
from getmail import upLoadAttatchment
from typing import List
from pydantic import BaseModel
import msal
import uvicorn

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


# 建立一個basemodel
class Task(BaseModel):
    taskID: str
    token: str
    message_list: List[str]


@app.post("/task")
async def create_task(task: Task) -> str:
    """give sufficient information and it will upload specific attatchment to minIO

    Args:
        task (Task): contain taskID(str), token(str) and message_list(List[str])

    Returns:
        str: task id
    """
    for message in task.message_list:
        upLoadAttatchment(token=task.token,taskID=task.taskID,MessageID=message)
    
    return task.taskID

@app.get("/checkTask")
def checkTask(taskID:str) -> bool:
    """check wheather the task is done, it check the column isbad == None in database

    Args:
        taskID (str): the task id specific on front-end

    Returns:
        bool: wheather the task is done
    """
    rows = t_pysql.getTaskData(taskID)
    for row in rows:
        if row[2] == None:
            return False
    return True

@app.get("/showResult")
def showResult(taskID:str):
    rows = t_pysql.getyaraResult(taskID)
    return rows

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)