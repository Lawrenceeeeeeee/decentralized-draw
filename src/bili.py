import httpx
import re
import urllib.parse
import json
import time
from functools import reduce
from hashlib import md5
import browser_cookie3
import toml

# 读取配置文件
config = toml.load("config.toml")

cookies = browser_cookie3.load(domain_name='bilibili.com')
cookie_str = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cookies])

headers = {
    "User-Agent": config["User-Agent"],
    "Referer": "https://www.bilibili.com/",
    "Cookie": cookie_str,
}
dynamic_url = "https://space.bilibili.com/946974/dynamic"

text = httpx.get(dynamic_url, headers=headers).text

# <script id="__RENDER_DATA__" type="application/json">xxx</script>
__RENDER_DATA__ = re.search(
    r"<script id=\"__RENDER_DATA__\" type=\"application/json\">(.*?)</script>",
    text,
    re.S,
).group(1)

access_id = json.loads(urllib.parse.unquote(__RENDER_DATA__))["access_id"]

# wbi 签名
mixinKeyEncTab = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]


def getMixinKey(orig: str):
    "对 imgKey 和 subKey 进行字符顺序打乱编码"
    return reduce(lambda s, i: s + orig[i], mixinKeyEncTab, "")[:32]


def encWbi(params: dict, img_key: str, sub_key: str):
    "为请求参数进行 wbi 签名"
    mixin_key = getMixinKey(img_key + sub_key)
    curr_time = round(time.time())
    params["wts"] = curr_time  # 添加 wts 字段
    params = dict(sorted(params.items()))  # 按照 key 重排参数
    # 过滤 value 中的 "!'()*" 字符
    params = {
        k: "".join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v in params.items()
    }
    query = urllib.parse.urlencode(params)  # 序列化参数
    wbi_sign = md5((query + mixin_key).encode()).hexdigest()  # 计算 w_rid
    params["w_rid"] = wbi_sign
    return params


def getWbiKeys() -> tuple[str, str]:
    "获取最新的 img_key 和 sub_key"
    headers = {
        "User-Agent": config["User-Agent"],
        "Referer": "https://www.bilibili.com/",
    }
    resp = httpx.get("https://api.bilibili.com/x/web-interface/nav", headers=headers)
    resp.raise_for_status()
    json_content = resp.json()
    img_url: str = json_content["data"]["wbi_img"]["img_url"]
    sub_url: str = json_content["data"]["wbi_img"]["sub_url"]
    img_key = img_url.rsplit("/", 1)[1].split(".")[0]
    sub_key = sub_url.rsplit("/", 1)[1].split(".")[0]
    return img_key, sub_key


def bili_api_request(url: str, params: dict) -> dict:
    img_key, sub_key = getWbiKeys()

    # 在params中添加web_location、w_webid字段
    params["web_location"] = 333.999
    params["w_webid"] = access_id
    
    signed_params = encWbi(
        params=params,
        img_key=img_key,
        sub_key=sub_key,
    )
    
    query = urllib.parse.urlencode(signed_params)

    resp = httpx.get(f"{url}?{query}", headers=headers)
    return resp.json()

if __name__ == "__main__":
    params = {
        "mid": 149385276,
    }
    url = "https://api.bilibili.com/x/space/wbi/acc/info"
    res = bili_api_request(url, params)
    # print(res)
    print(f"用户等级：{res['data']['level']}")