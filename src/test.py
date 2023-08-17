# # from fastapi import FastAPI, UploadFile, File, HTTPException

# import os
# import zipfile

# # app = FastAPI()

# # Initialize GCS


# # @app.post("/upload/")
# # async def upload_file(file: UploadFile = File(...)):
#     # try:
#         # Read the uploaded file
#         # file_content = await file.read()
        
#         # Create a blob in the bucket and upload the file


# #file = UploadFile()
taskID = "dcb9ee1b-4a55-4e16-a2fd-363bcdd417e4"
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

def upLoadToGCP(taskID,outputfiles=outputfiles,):
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

unzip_upload_gcp(taskID=taskID,outputfiles=["Logfile.csv"])

#testlist = {"a38fcb6f-0ddb-4daa-b10c-ce35e1504f85":{"filename":"OV7670_2006.pdf","createTime":"2023-08-16T06:25:09.909974","status":"init"},"5a6731d2-918a-4b66-9d8e-6b2bb044b10b":{"filename":"OV7670_2006.pdf","createTime":"2023-08-16T06:26:34.640303","status":"init"}}

