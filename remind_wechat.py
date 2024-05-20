import pickle
from threading import Thread
import time
import requests
from io import BytesIO
from PIL import Image
import os

requests.packages.urllib3.disable_warnings()

headers ={
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    'Referer': "https://mp.weixin.qq.com/",
    "Host": "mp.weixin.qq.com"
}

class showpng(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data

    def run(self):
        img = Image.open(BytesIO(self.data))
        img.show()

def islogin(session):
    try:
        session.cookies.load(ignore_discard=True)
    except Exception:
        pass
    loginurl = session.get("https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1").json()
    if loginurl['base_resp']['ret'] == 0:
        print('Cookies valid, No login again!')
        # print("loginurl:", loginurl)
        return session, True
    else:
        print('Cookies invalid, please scan the code!')
        return session, False

# acquire contacts and send messages to openId
def getOpenIdAndSendMsg(session, openId, msg):
    # acquire token
    token = session.cookies.get("token")
    contact_url = session.get("https://mp.weixin.qq.com/cgi-bin/user_tag?action=get_all_data&lang=zh_CN&token=%s" % token)
    # print("contact_url:", contact_url.text)

    # https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&f=json
    # type=1&tofakeid=okyJOv0JvPA42SvzcS-3qxPE2brI&quickReplyId=&imgcode=&content=test&token=1545128531&lang=zh_CN&f=json&ajax=1
    send_url = "https://mp.weixin.qq.com/cgi-bin/singlesend?t=ajax-response&f=json"
    dataJson = {
        "type": 1,
        "tofakeid": openId,
        "quickReplyId": '',
        "imgcode": '',
        "content": msg,
        "token": token,
        "lang": "en_US",
        "f": "json",
        "ajax": 1
    }
    # data = "type=1&tofakeid=%s&quickReplyId=&imgcode=&content=%s&token=%s&lang=zh_CN&f=json&ajax=1" % (openId, msg, token)
    res_send = session.post(send_url,
                            data=dataJson,
                            headers=headers).json()
    print("res_send", res_send)

# login offical account
def official_login():

    session = requests.session()
    session.get('https://mp.weixin.qq.com/', headers=headers)
    session.post('https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin', data='userlang=zh_CN&redirect_url=&login_type=3&sessionid={}&token=&lang=zh_CN&f=json&ajax=1'.format(int(time.time() * 1000)), headers=headers)
    loginurl = session.get('https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={}'.format(int(time.time() * 1000)))
    dateurl = 'https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1'
    t = showpng(loginurl.content)
    t.start()
    while 1:
        date = session.get(dateurl).json()
        if date['status'] == 0:
            print('code invalid, please scan the code!')
        elif date['status'] == 6:
            print('please confirm!')
        if date['status'] == 1:
            print('confirm success, login success!')
            url = session.post('https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login', data='userlang=zh_CN&redirect_url=&cookie_forbidden=0&cookie_cleaned=1&plugin_used=0&login_type=3&token=&lang=zh_CN&f=json&ajax=1', headers=headers).json()
            print("url:", url)
            # Acquire the token and save it to cookies
            redirect_url = url["redirect_url"]

            token = redirect_url[redirect_url.rfind("=") + 1:len(redirect_url)]
            requests.utils.add_dict_to_cookiejar(session.cookies, {"token": token})
            # acquire contacts
            contact_url = session.get("https://mp.weixin.qq.com/cgi-bin/user_tag?action=get_all_data&lang=zh_CN&token=%s" % token)
            # print("contact_url:", contact_url.text)
            break
        time.sleep(2)
    with open('gzhcookies.cookie', 'wb') as f:
        pickle.dump(session.cookies, f)
    return session

def checkSession():
    # write cookie
    session = requests.session()
    if not os.path.exists('gzhcookies.cookie'):
        with open('gzhcookies.cookie', 'wb') as f:
            pickle.dump(session.cookies, f)
    # read cookie
    session.cookies = pickle.load(open('gzhcookies.cookie', 'rb'))
    session, status = islogin(session)
    if not status:
        session = official_login()

    return session

if __name__ == '__main__':

    # Send messages to the specified openId, maximum length of each message is 598
    openId = "oIAZG6FN5E74DJ6kvxO8J2fe04Oo" # replace with your openId
    msgIn = "Test again from Ubuntu"
    resTxtList = [msgIn]
    split_length = 598
    start_txt = 0
    end_txt = split_length
    session = checkSession()
    for msg in resTxtList:
        getOpenIdAndSendMsg(session, openId, msg)