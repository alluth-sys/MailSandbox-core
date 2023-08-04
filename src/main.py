from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from t_yamlReader import getyamlkey
import msal
import uvicorn

app = FastAPI()
host = "0.0.0.0"
port = 8777

@app.get("/login")
def login(request: Request):
    # 初始化 MSAL
    config = {
        "client_id": getyamlkey('graph_client'),  # 從環境變數取得 client_id
        "authority": "https://login.microsoftonline.com/common",
        "redirect_uri": "http://localhost:8777/callback",  # 將回調地址改為你 FastAPI 服務的一個路由
        "scope": ["https://graph.microsoft.com/.default"],
    }

    app = msal.PublicClientApplication(config['client_id'], authority=config['authority'])

    # 建立登入的 URL 並重定向用戶到該 URL
    auth_url = app.get_authorization_request_url(config['scope'], redirect_uri=config['redirect_uri'])
    return RedirectResponse(auth_url)


@app.get("/callback")
def callback(code: str):
    # 初始化 MSAL
    config = {
        "client_id": getyamlkey('graph_client'),
        "authority": "https://login.microsoftonline.com/common",
        "redirect_uri": "http://localhost:8777/callback",
        "scope": ["https://graph.microsoft.com/.default"],
    }

    app = msal.PublicClientApplication(config['client_id'], authority=config['authority'])

    # 使用授權碼獲取 token
    result = app.acquire_token_by_authorization_code(code, config['scope'], redirect_uri=config['redirect_uri'])
    
    if "access_token" in result:
        # 成功取得 token，返回結果（或進行其他處理）
        access_token = result['access_token']
        

        # TODO: 之後這邊應該會回傳到某一個地方
        return access_token
    else:
        # 取得 token 失敗，返回錯誤信息
        return HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=result.get('error_description', 'Unknown error'),
        )

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)