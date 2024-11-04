from src import bili, get_cookie
import requests
import time
from bilibili_api import Credential, user
import asyncio
from retry import retry

# 替换为你的SESSDATA和buvid3（若需要）
cookie_info = get_cookie.extract_cookie(platform="safari")

credential = Credential(sessdata=cookie_info['SESSDATA'], buvid3=cookie_info['buvid3'], bili_jct=cookie_info['bili_jct'], dedeuserid=cookie_info['DedeUserID'])

@retry(tries=3, delay=1)
def following_me(uid: int, me: int = None) -> bool:
    current_user = user.User(uid=uid, credential=credential)
    
    # 强制同步执行异步方法
    lists = asyncio.run(current_user.get_all_followings())
    
    if not me:
        me = int(cookie_info['DedeUserID'])
    # 检查是否在列表中
    if me in lists:
        return True
    else:
        return False

def get_user_level(uid: int) -> dict:
    params = {
        "mid": uid,
    }
    url = "https://api.bilibili.com/x/space/wbi/acc/info"
    res = bili.bili_api_request(url, params)
    # print(type(res['data']['level']))
    return res['data']['level']

if __name__ == "__main__":
    # 请替换为你的UID
    uid = 96496054
    print(get_user_level(uid))