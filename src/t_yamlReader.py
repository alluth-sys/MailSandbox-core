import os
import yaml

# 獲取當前目錄的上一級目錄
parent_dir = os.path.dirname(os.path.abspath(__file__))

# 構建完整的文件路徑
config_file_path = os.path.join(parent_dir, 'config.yaml')

# 讀取yaml檔案的內容
with open(config_file_path, 'r') as config_file:
    config = yaml.safe_load(config_file)

def getyamlkey(keyName):
    return config[keyName]
