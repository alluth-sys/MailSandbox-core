# import os
# import json
# from unittest.mock import Mock, patch
# from getmail import getMessageValue
# from datetime import datetime

# mail = getMessageValue(messageID="AQMkADAwATM3ZmYAZS1kNGY3LWZhNTMtMDACLTAwCgBGAAADY9XFoJ43pEe2TYRuW9aNfAcAafGhIvVpyk_198HMOQEhIwAAAgEMAAAAafGhIvVpyk_198HMOQEhIwAFGsOrOgAAAA==",
#                        token='EwB4A8l6BAAUAOyDv0l6PcCVu89kmzvqZmkWABkAAZZVGu8LKHX1umubDCWpJWnELin7xrPqjt6epb1YzwM7pKNt/ltkjOyMvO4Tdc5eNrHhRhbGxfWnCXwE96Zft21Benjbk4uCuCnAB71xQvu+j9aK+hWaOpGcQAiBDteNC59OJBBq3fM1pJK74iekrPt9/FC++kSVRYHCXpOKNrWWQz+ImgiPAxpSu/yI7j3h3KudpR/ytBEMSz6ZlDs+8/RQHKwY6v8J621jRLac5hyZpdv4y63oDUhoJnOwwlVdZ7p6DcqnyoplVxDxSj1TZti1rjhnDcNhbcPgZdakOM8MH/oOTS/9RczXbCGUtDzs5N2qsj52k7ONNzdFQB+UrU8DZgAACHC3Mfz7avYRSALvc1agVHi0SVkBVKHnogWiTqsSTwtBGoDYB2v75wPImC+RUgobFL2lC/QcrJRlnU4SBgXIV8B2dZyseHbJfgF79AKoYSsPMi++HSeVk4aZFxJhsYQfr2fBndDy8j3qikpCWPsy/WWlewkED2VafNI3aulO7dVLyrlVANCEaVZYzoX+E7MX+utexEKnZI3SoJx69vJbUFcOEaF0QT0exchXJuEeMBso/1SknDzL/c83lC1WxrC419+Ts6yO/vwb30rv85ppueAlrz8A59BO78K6SOxFivbvA/FNLNxaxzUjFf3A9Wc8q6mLDIiTp+vwdTnvVySAAq/vbqzIkDwKkIXxrM0/FsSvPb378oA3aQRAJZGUy0huSt1RsBdI5n3uTdK5UAyYOipCkUDinmHDb2O6OFJyU22ls9S3fdpZHwVi7fmMKXoN29hz8oxLEDAhN551ddbeLPW6+kt5S87a8ExhRcP63+YwxExlaviYYZlCResfoghayavET9+qXhNQPTk8rmyFZc1Q7fsa75X3b9Q0Q8wd4Y4GKbQwh4EYfAwkzzMa3I6+leNy0Dy0DQMsca61faLmYAjYssUMxliAH232COAPVdnYGMLYmR6OXaL6jmQXVDbt6gO5D0OSZt4VPc5ZQ43zQZOzYzTtw9r/9QCjGirp5DL/qA7eH2r7PM6XeZDXbX9P37e5DNEaPm/HdXju/UThxnOT+KFbq1q6cpcTkF0DIH4f3jQ9kQ8TF8Ugmrrdxq6yD8BBoDYYySQRFnJ3GKfhqaAFcocC')

# if "error" in mail:
#     print("Hi")
# else:
#     received_datetime = datetime.strptime(mail['receivedDateTime'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

#     #把信件的值取出
#     MessageID, Subject, Received, Sender= \
#         mail['id'],mail['subject'], received_datetime, mail['from']['emailAddress']['address']

#     # 假如不在那就加入資料庫並且繼續掃描
#     print(MessageID, Subject, Received,Sender)

data = '123'

print(data[0:20])