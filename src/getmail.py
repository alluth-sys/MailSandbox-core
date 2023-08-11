"""
This code provide some funciton to get mail information from outlook incloud mail detail and attatchment
and can send mail to minIO
"""

#from t_graphtoken import getToken
import t_minIO
import requests
import base64
import t_pysql
from datetime import datetime

def getHeader(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    return headers

"""
def getMail(token):
    url = 'https://graph.microsoft.com/v1.0/me/mailfolders/inbox/messages'
    # access設定認證
    headers = getHeader(token)
    
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
"""

## list mail
def listMailInfo(token,top=100,skip=0) -> list:
    """
    Get a list of mails

    Args:
        token (_type_): token to use graph API
        top (int, optional): mail limit. Defaults to 100.
        skip (int, optional): skip mail. Defaults to 0.

    Returns:
        list: a list of mails which like messageValue.json in appendix
    """

    url = 'https://graph.microsoft.com/v1.0/me/mailfolders/inbox/messages'

    # access設定認證
    headers = getHeader(token)

    # 設定抓取信件的rule，詳細參考parameter.md in appendix
    params = {
        '$top': top,  # Limit to 100 messages
        '$skip': skip,
        #'$filter':100,
        #'$orderBy':100,
        #'$select':100
    }
    # 得到response

    response = requests.get(url, headers=headers, params=params)
    mails = []
    for message in response.json()['value']:
        mails.append(message)
    return mails

## list mail attatchments
def listMailattatchment(token:str,messageID:str,\
    getHeader = getHeader) -> list:
    """get a list of attatchments about specific messageID

    Args:
        messageID (str): the mail id in outlook

    Returns:
        list: a list of attatchments information which like attatchmentValue.json in appendix
    """
    attachment_url = f"https://graph.microsoft.com/v1.0/me/messages/"+messageID+"/attachments"
    headers = getHeader(token)
    attachment_response = requests.get(attachment_url, headers=headers)

    # 得到attachment的value們，要再進一步拆解
    attachments = attachment_response.json()['value']
    goodAttatchments = []
    for attachment in attachments:
        if attachment['@odata.type'] == '#microsoft.graph.fileAttachment':
            goodAttatchments.append(attachment)
    return goodAttatchments

def upLoadAttatchment(token,taskID,messageID,listMailattatchment = listMailattatchment,\
                        uploadFile = t_minIO.uploadFile,\
                        insert_attData = t_pysql.insert_attDataTask):
    """把某一個message的所有attatchment丟上去

    Args:
        token (_type_): _description_
        taskID (_type_): _description_
        MessageID (_type_): _description_
        listMailattatchment (_type_, optional): _description_. Defaults to listMailattatchment.
    """
# 取得所有attatchment
    attachments = listMailattatchment(token,messageID)
    for attachment in attachments:
        import re
        print(attachment['name'])
        name = re.sub(r'[^\w\._]', '_', attachment['name'])
        print(name)
        name = name.replace('.','_')
        name = name.replace('__','_')
        name = name[0:20]
        attachment_content = base64.b64decode(attachment['contentBytes'])
        # 把附件放到minIO
        upresult = uploadFile(attachment_content,messageID + name)
        if upresult == 'error':
            return "cannot upload "+name
        # 把附件訊息放到sql
        #insert_attData(MessageID,attachment['name'],MessageID+attachment['name'])
        insert_attData(messageID,name,messageID+name,taskID)
    return "Done"

#TODO: 有可能會抓錯，例如token壞掉
def getMessageValue(token:str,messageID:str,getHeader=getHeader):
    """把mailID給予這個函數，輸出Graph API回傳的mail json value

    Args:
        token (str): _description_
        messageID (str): _description_
        getHeader (_type_, optional): _description_. Defaults to getHeader.

    Returns:
        _type_: _description_
    """
    url = 'https://graph.microsoft.com/v1.0/me/mailfolders/inbox/messages/'+messageID

    # access設定認證
    headers = getHeader(token)

    response = requests.get(url, headers=headers)
    mail = response.json()
    if "error" in mail:
        raise ValueError('error in request GraphAPI!' + str(mail["error"]))
    return mail

def getMailProperty(mailValue:str):
    received_datetime = datetime.strptime(mailValue['receivedDateTime'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

    #把信件的值取出
    MessageID, Subject, Received, Sender= \
        mailValue['id'],mailValue['subject'], received_datetime, mailValue['from']['emailAddress']['address']

    # 假如不在那就加入資料庫並且繼續掃描
    return (MessageID, Subject, Received, Sender)

def getMail(token:str,\
    listMailInfo=listMailInfo,\
    check_duplicate_id = t_pysql.check_duplicate_id,\
    insert_maildata = t_pysql.insert_maildata,\
    insert_attData = t_pysql.insert_attData,\
    listMailattatchment = listMailattatchment,\
    uploadFile = t_minIO.uploadFile):
    """
    send mail to minIO, it's a big couple of method here

    Args:
        token (str): token which to use graph api
    """
    mails = listMailInfo(token)
    for mail in mails:
        # 把時間轉換為datatime
        #print(mail.keys())
        #received_datetime = datetime.strptime(mail['receivedDateTime'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

        #把信件的值取出
        MessageID, Subject, Received, Sender= \
            getMailProperty(mail)

        #把id抓下來跟資料庫比對
        if check_duplicate_id(MessageID):
            # 假如有在id那就跳過
            continue
        # 假如不在那就加入資料庫並且繼續掃描
        insert_maildata(MessageID, Subject, Received,Sender)

        # 取得所有attatchment
        attachments = listMailattatchment(MessageID)
        for attachment in attachments:
            attachment_content = base64.b64decode(attachment['contentBytes'])
            # 把附件放到minIO
            uploadFile(attachment_content,MessageID+attachment['name'])
            # 把附件訊息放到sql
            insert_attData(MessageID,attachment['name'],MessageID+attachment['name'])