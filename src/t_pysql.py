import mysql.connector
from mysql.connector.connection import MySQLConnection
from t_yamlReader import getyamlkey

def create_connection() -> MySQLConnection:
    """
    Establish and return a connection to a MySQL database.

    This function retrieves the database username and password from the 'getyamlkey' function
    in the 't_yamlReader' module, and attempts to establish a connection to the 'outlookScan'
    database on the 'db' host using this information.

    Returns:
        MySQLConnection: An open connection to the database.
    """
    connection = mysql.connector.connect(
        host="db",
        user=getyamlkey('dbuser'),
        password=getyamlkey('dbpassword'),
        database="outlookScan"
    )
    return connection

# 檢查是否有重複的 ID
def check_duplicate_id(id):
    conn = create_connection()
    cursor = conn.cursor()

    query = "SELECT MessageID FROM mail WHERE MessageID = %s"
    cursor.execute(query, (id,))

    result = cursor.fetchone()
    if result:
        print("ID already exists.")
        result = True
    else:
        print("ID does not exist.")
        result = False

    cursor.close()
    conn.close()
    return result

# 新增mail資料到資料庫(原本的版本)
def insert_maildata(MessageID, Subject, Received,Sender):
    conn = create_connection()
    cursor = conn.cursor()

    query = "INSERT INTO mail (MessageID, Subject, Received,Sender) VALUES (%s, %s, %s, %s)"
    values = (MessageID, Subject, Received, Sender)

    cursor.execute(query, values)
    conn.commit()

    print("Data inserted successfully.")

    cursor.close()
    conn.close()

# 新增attatch資料到資料庫(原本的版本)
def insert_attData(MessageID,AttatchmentName,ID):
    conn = create_connection()
    cursor = conn.cursor()

    query = "INSERT INTO attatchment (MessageID,AttatchmentName,ID) VALUES (%s,%s,%s)"
    values = (MessageID,AttatchmentName,ID)

    cursor.execute(query, values)
    conn.commit()

    print("Data inserted successfully.")

    cursor.close()
    conn.close()

# 新增attatch資料（有task的版本）到資料庫
def insert_attDataTask(MessageID,AttatchmentName,ID,TaskID):
    conn = create_connection()
    cursor = conn.cursor()

    query = "INSERT INTO attatchmentTask (MessageID,AttatchmentName,ID,TaskID) VALUES (%s, %s, %s, %s)"
    values = (MessageID,AttatchmentName,ID,TaskID)

    cursor.execute(query, values)
    conn.commit()

    print("Data inserted successfully.")

    cursor.close()
    conn.close()

def insert_userTask(userID,taskID):
    conn = create_connection()
    cursor = conn.cursor()

    query = "INSERT INTO user_task (userID,taskID) VALUES (%s, %s)"
    values = (userID,taskID)

    cursor.execute(query, values)
    conn.commit()

    print("Data inserted successfully.")

    cursor.close()
    conn.close()

def getTaskByUser(userID):
    conn = create_connection()
    cursor = conn.cursor()

    # Query for task 'ttttt'
    task_query = """
        SELECT * 
        FROM user_task 
        WHERE userID = %s
    """
    cursor.execute(task_query, (userID,))
    rows = []
    for row in cursor:
        rows.append(row)
    conn.close()
    return rows

def getFileIDByTask(taskID):
    conn = create_connection()
    cursor = conn.cursor()

    # Query for task 'ttttt'
    task_query = """
        SELECT ID, AttatchmentName, TaskID 
        FROM attatchmentTask 
        WHERE TaskID = %s
    """
    cursor.execute(task_query, (taskID,))
    rows = []
    for row in cursor:
        rows.append(row)
    conn.close()
    return rows

# 取得attatchmentTask 這個表格符合TaskID的所有內容
def getTaskData(TaskID):
    conn = create_connection()
    cursor = conn.cursor()

    # Query for task 'ttttt'
    task_query = """
        SELECT * 
        FROM attatchmentTask 
        WHERE TaskID = %s
    """
    cursor.execute(task_query, (TaskID,))
    rows = []
    for row in cursor:
        rows.append(row)
    conn.close()
    return rows

def getyaraResultByFileID(fileID):
    conn = create_connection()
    cursor = conn.cursor()
    # Query for 'isBad' = 1 and join with 'yara_result'
    is_bad_query = """
        SELECT * 
        FROM yara_result 
        WHERE ID = %s
    """
    cursor.execute(is_bad_query, (fileID,))
    rows = []
    for row in cursor:
        rows.append(row)
    conn.close()
    return rows

# 取得attatchmentTask跟yararesult JOIN的結果
def getyaraResult(taskID):
    conn = create_connection()
    cursor = conn.cursor()
    # Query for 'isBad' = 1 and join with 'yara_result'
    is_bad_query = """
        SELECT yr.* 
        FROM attatchmentTask at 
        JOIN yara_result yr ON at.ID = yr.ID 
        WHERE at.isBad = 1 AND at.TaskID = %s
    """
    cursor.execute(is_bad_query, (taskID,))
    rows = []
    for row in cursor:
        rows.append(row)
    conn.close()
    return rows

# 更新資料
def updateIsbad(id,value):
    conn = create_connection()
    cursor = conn.cursor()

    # 更新isbad
    update_query = "UPDATE attatchment SET isBad = %s WHERE ID = %s"
    values = (value, id)
    cursor.execute(update_query, values)
    conn.commit()

    print("Data inserted successfully.")

    cursor.close()
    conn.close()

# 把yara結果放進yara_result表格
def insert_scanResult(filename,match):
    conn = create_connection()
    cursor = conn.cursor()

    query = "INSERT INTO yara_result (ID,yara) VALUES (%s, %s)"
    values = (filename,match)

    cursor.execute(query, values)
    conn.commit()

    print("Data inserted successfully.")

    cursor.close()
    conn.close()