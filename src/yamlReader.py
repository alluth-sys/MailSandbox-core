import yaml

# 加载 config.yaml 文件中的配置项
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

def getyamlkey(keyName):
    return yaml.safe.load(keyName)