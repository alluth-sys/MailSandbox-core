from t_graphtoken import getToken
key = getToken()
import t_minIO
import requests
import base64
import t_pysql
from datetime import datetime

# 用graph api把信件發過來
access_token = key
obj_id = '03ab3b96-cf0a-4e57-983e-9eb7b0ffc7a5'
url = 'https://graph.microsoft.com/v1.0/me/mailfolders/inbox/messages'
#url = 'https://graph.microsoft.com/v1.0/users/'+obj_id+'/mailfolders/inbox/messages'
# access設定認證
headers = {
    'Authorization': f'Bearer {access_token}',
}
# 設定抓取信件的rule
params = {
    '$top': 100,  # Limit to 100 messages
}
# 得到response

response = requests.get(url, headers=headers, params=params)
print(response.json())

# 解析回應並印出每封郵件的相關資訊
for message in response.json()['value']:
    print(f"Subject: {message['subject']}")
    print(f"Received: {message['receivedDateTime']}")
    print(f"From: {message['from']['emailAddress']['address']}")
    print(f"Message ID: {message['id']}")
    #把信件的值取出
    MessageID = message['id']
    Subject = message['subject']
    # 把時間轉換為datatime
    received_datetime = datetime.strptime(message['receivedDateTime'], "%Y-%m-%dT%H:%M:%SZ")
    # 把datatime換成mysql喜歡的格式
    Received = received_datetime.strftime("%Y-%m-%d %H:%M:%S")
    Sender = message['from']['emailAddress']['address']

    #把id抓下來跟資料庫比對
    if t_pysql.check_duplicate_id(MessageID):
        # 假如有在id那就跳過
        continue
    # 假如不在那就加入資料庫並且繼續掃描
    t_pysql.insert_maildata(MessageID, Subject, Received,Sender)

    # 獲取郵件的附件，一樣使用url去抓，主要用message id 去搞
    attachment_url = f"https://graph.microsoft.com/v1.0/me/messages/{message['id']}/attachments"
    attachment_response = requests.get(attachment_url, headers=headers)
    # 得到attachment的value們，要再進一步拆解
    attachments = attachment_response.json()['value']

    for attachment in attachments:
        if attachment['@odata.type'] == '#microsoft.graph.fileAttachment':
            # 下載附件
            attachment_content = base64.b64decode(attachment['contentBytes'])
            
            #儲存到本地
            # path = os.path.join('./fileSave', attachment['name'])
            # with open(path, 'wb') as f:
            #     f.write(attachment_content)
            
            # 把附件放到minIO
            t_minIO.uploadFile(attachment_content,MessageID+attachment['name'])
            # 把附件訊息放到sql
            t_pysql.insert_attData(MessageID,attachment['name'],MessageID+attachment['name'])

    print("\n")