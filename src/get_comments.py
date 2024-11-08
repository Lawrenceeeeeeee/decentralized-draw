import requests
import os
import src.bvav as bvav
import json
import time
import pandas as pd
import browser_cookie3
from src import get_cookie as gc
import toml

config = toml.load("config.toml")

columns = ['oid','timestamp', 'rpid', 'uid', 'uname', 'content', 'likes', 'replies']

def get_comments(type, oid, sort=0, nohot=0, ps=20, pn=1):
    
    """获取b站视频评论

    Args:
        type (_type_): _description_
        oid (_type_): _description_
        sort (int, optional): _description_. Defaults to 0.
        nohot (int, optional): _description_. Defaults to 0.
        ps (int, optional): _description_. Defaults to 20.
        pn (int, optional): _description_. Defaults to 1.
    """
    
    url = "https://api.bilibili.com/x/v2/reply"
    
    params = {
        "type": type,
        "oid": oid,
        "sort": sort,
        "nohot": nohot,
        "ps": ps,
        "pn": pn,
    }
    
    try:    
        cookies = browser_cookie3.load(domain_name='bilibili.com')
        cookie_str = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cookies])
    except Exception as e:
        print(f"获取cookies失败，尝试读取config.toml中的cookies")
        cookie_str = gc.cookies_from_config()
    
    headers = {
        "User-Agent": config['User-Agent'],
        "Referer": "https://www.bilibili.com/",
        "Cookie": cookie_str,
    }
    response = requests.get(url, params=params, headers=headers, cookies=cookies)
    
    # Check if the request was successful
    if response.status_code == 200:
        df = pd.DataFrame(columns=columns)
        # Print the content of the response (body)
        results = json.loads(response.text)
        
        if results['code'] != 0:
            print("Failed to fetch data. Error message:", results['message'])
            return None
        for result in results['data']['replies']:
            new_row = {
                'oid': oid,
                'timestamp': result['ctime'],
                'rpid': result['rpid'], # 'rpid_str': '0', 'root': '0', '
                'uid': result['mid'],
                'uname': result['member']['uname'],
                'content': result['content']['message'],
                'likes': result['like'],
                'replies': result['count'],
            }
            new_row = pd.DataFrame(new_row, index=[0])
            df = pd.concat([df, new_row], ignore_index=True)
            
        return df
    else:
        print("Failed to fetch data. Status code:", response.status_code)
        return None
   
     
def get_full_comments(type, bv, sort=0, nohot=0, ps=20, sample_size=None):
    """获取指定b站视频所有评论

    Args:
        type (_type_): 评论区类型代码
        bv (_type_): 视频bv号
        sort (int, optional): 排序方式，默认为0。0：按时间；1：按点赞数；2：按回复数.
        nohot (int, optional): 是否不显示热评. 默认为0.
        ps (int, optional): 每页项数（1-20）. Defaults to 20.

    Returns:
        _type_: _description_
    
    ## 评论区类型代码
        
    （PS：以下部分内容来源不明，有待验证）

    | 代码 | 评论区类型              | oid 的意义  |
    | ---- | ----------------------- | ----------- |
    | 1    | 视频稿件                | 稿件 avid   |
    | 2    | 话题                    | 话题 id     |
    | 4    | 活动                    | 活动 id     |
    | 5    | 小视频                  | 小视频 id   |
    | 6    | 小黑屋封禁信息          | 封禁公示 id |
    | 7    | 公告信息                | 公告 id     |
    | 8    | 直播活动                | 直播间 id   |
    | 9    | 活动稿件                | (?)         |
    | 10   | 直播公告                | (?)         |
    | 11   | 相簿（图片动态）        | 相簿 id     |
    | 12   | 专栏                    | 专栏 cvid   |
    | 13   | 票务                    | (?)         |
    | 14   | 音频                    | 音频 auid   |
    | 15   | 风纪委员会              | 众裁项目 id |
    | 16   | 点评                    | (?)         |
    | 17   | 动态（纯文字动态&分享） | 动态 id     |
    | 18   | 播单                    | (?)         |
    | 19   | 音乐播单                | (?)         |
    | 20   | 漫画                    | (?)         |
    | 21   | 漫画                    | (?)         |
    | 22   | 漫画                    | 漫画 mcid   |
    | 33   | 课程                    | 课程 epid   |
    """

    page = 1
    df = pd.DataFrame(columns=columns)
    oid = bvav.bv2av(bv)

    while True:
        try:
            res = get_comments(type, oid, sort, nohot, ps, page)
        except Exception as e:
            print("Failed to fetch data. Error message:", e)
            print(str(e))
            break
        if res is None:
            break
        if res.empty:
            break
        df = pd.concat([df, res], ignore_index=True)
        page += 1
        # time.sleep(1) # 如果被ban了就取消这个注释
        
    if sample_size and sample_size < df.shape[0]:
        df = df.sample(n=sample_size)
    
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # # 保存原始工作目录
    # original_cwd = os.getcwd()
    # # 更改工作目录到函数所在文件目录
    # os.chdir(current_dir)
    # with open(f'temp/{bv}.csv', 'a') as f:
    #     df.to_csv(f, header=True, encoding='utf-8')
    return df


# print(len(comment_list))

if __name__ == "__main__":
    # print(get_comments('1', av, 0, 0, 20, 1))
    bv = "BV1bc411f7fK"
    df = get_full_comments('1', bv)
    df.to_csv(f'{bv}_comments.csv', header=True, encoding='utf-8')
    # print(get_comments('1', av, 0, 0, 20, 1))
# print(get_comments('1', av, 0, 0, 20, 1))