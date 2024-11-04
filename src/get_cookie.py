import browser_cookie3
import requests

def get_cookie(platform: str = "safari") -> dict:
    # 从Safari浏览器中读取B站的Cookie
    try:
        # 读取 bilibili.com 域名的 Cookie
        if platform == "safari":
            cookies = browser_cookie3.safari(domain_name="bilibili.com")
        elif platform == "chrome":
            cookies = browser_cookie3.chrome(domain_name="bilibili.com")
        elif platform == "firefox":
            cookies = browser_cookie3.firefox(domain_name="bilibili.com")
        else:
            print("未知的浏览器类型")
            cookies = None
    except Exception as e:
        print(f"读取 Safari 浏览器 Cookie 失败: {e}")
        cookies = None

    return cookies

def extract_cookie(platform: str = "safari") -> dict:
    
    cookies = get_cookie(platform)
    
    # 提取特定的 Cookie 值
    sessdata = None
    buvid3 = None
    bili_jct = None
    dedeuserid = None

    if cookies:
        for cookie in cookies:
            # 查找并提取指定的 Cookie
            if cookie.name == "SESSDATA":
                sessdata = cookie.value
            elif cookie.name == "buvid3":
                buvid3 = cookie.value
            elif cookie.name == "bili_jct":
                bili_jct = cookie.value
            elif cookie.name == "DedeUserID":
                dedeuserid = cookie.value
    else:
        print("未能从浏览器读取到有效的 Cookie 信息")

    return {
        "SESSDATA": sessdata,
        "buvid3": buvid3,
        "bili_jct": bili_jct,
        "DedeUserID": dedeuserid
    }

if __name__ == "__main__":
    print(extract_cookie())