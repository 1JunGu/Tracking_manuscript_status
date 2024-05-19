import requests
import time

# 替换为您的AppID和AppSecret
APPID = 'wxcfd35ad831a00eb6'
APPSECRET = 'a22691a6196b3f0e0e47cacad8531540'

# 获取access token
def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'
    response = requests.get(url)
    return response.json()['access_token']

# 发送消息
def send_message(to_user, message):
    access_token = get_access_token()
    url = f'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}'
    data = {
        "touser": to_user,
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    requests.post(url, json=data)

# 使用示例
if __name__ == '__main__':
    user = 'oIAZG6FN5E74DJ6kvxO8J2fe04Oo'  # 替换为接收消息的用户的OpenID
    message = '您的状态信息更新了！'
    send_message(user, message)

