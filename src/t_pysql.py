import mysql.connector
from t_yamlReader import getyamlkey

# 建立資料庫連線
def create_connection():
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

# 新增資料到資料庫
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

#把task的東西弄好
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

def getyaraResult(AttID):
    conn = create_connection()
    cursor = conn.cursor()
    # Query for 'isBad' = 1 and join with 'yara_result'
    is_bad_query = """
        SELECT yr.* 
        FROM attatchmentTask yt 
        JOIN yara_result yr ON yt.ID = yr.ID 
        WHERE yt.isBad = %s
    """
    cursor.execute(is_bad_query, (1,))
    conn.close()
    for row in cursor:
        print(row)
    return cursor

def insert_attData(MessageID,AttatchmentName,ID):
    conn = create_connection()
    cursor = conn.cursor()

    query = "INSERT INTO attatchment (MessageID,AttatchmentName,ID) VALUES (%s, %s,%s)"
    values = (MessageID,AttatchmentName,ID)

    cursor.execute(query, values)
    conn.commit()

    print("Data inserted successfully.")

    cursor.close()
    conn.close()

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