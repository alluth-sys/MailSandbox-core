import os
import json
from unittest.mock import Mock
from getmail import getMail,listMailattatchment,listMailInfo

def test_getMail():
    # 獲取當前目錄的上一級目錄
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 構建完整的文件路徑
    att_file_path = os.path.join(root_dir, 'appendix', 'attachmentValue.json')
    mail_file_path = os.path.join(root_dir, 'appendix', 'messageValue.json')

    # 讀取JSON文件的內容
    with open(att_file_path, 'r') as f:
        attatchmentValue = json.load(f)

    # 讀取JSON文件的內容
    with open(mail_file_path, 'r') as f:
        mailValue = json.load(f)
    
    # 定義一個token來用於測試
    test_token = "test_token"

    listMailInforeturn = []
    listMailInforeturn.append(mailValue)
    mock_listMailattatchmentreturn = []
    mock_listMailattatchmentreturn.append(attatchmentValue)

    # 使用Mock對象來模擬函數
    mock_listMailInfo = Mock(return_value=listMailInforeturn)
    mock_check_duplicate_id = Mock(return_value=False)
    mock_insert_maildata = Mock()
    mock_insert_attData = Mock()
    mock_listMailattatchment = Mock(return_value=mock_listMailattatchmentreturn)
    mock_uploadFile = Mock()
        
    getMail(token = test_token, \
            listMailInfo=mock_listMailInfo,\
            check_duplicate_id=mock_check_duplicate_id,\
            insert_maildata=mock_insert_maildata,\
            insert_attData=mock_insert_attData,\
            listMailattatchment=mock_listMailattatchment,\
            uploadFile=mock_uploadFile)

    # 在這裡添加assertions來驗證結果
    # 例如檢查某個函數是否被調用，或者被調用的次數等等
    mock_listMailInfo.assert_called_once_with(test_token)
    mock_uploadFile.assert_called_once()

