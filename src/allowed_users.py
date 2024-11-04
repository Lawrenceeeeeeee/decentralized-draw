import pandas as pd
import time
import random
from retry import retry
from tqdm import tqdm

from src import get_user_info as gui


@retry(delay=1, backoff=2)
def is_allowed(uid: int, me: int = None, follow=True, level=True) -> bool:
    '''
    判断是否允许抽奖
    '''
    try:
        # 如果不是粉丝则跳过
        if follow:
            if not gui.following_me(uid, me):
                return False
        
        # 如果等级不够则跳过    
        if level: 
            if gui.get_user_level(uid) < 3:
                return False
        
        return True
    except Exception as e:
        print(f"检测{uid}资格时出现错误。\nError message:", str(e))
        if str(e) == 'level':
            raise
        else:
            return False

def extract_allowed_comments(df: pd.DataFrame, me: int = None, follow=True, level=True) -> pd.DataFrame:
    '''
    提取允许抽奖的评论
    '''
    uids = df['uid'].unique()
    for uid in tqdm(uids, desc="检查抽奖资格"):
        try:
            if not is_allowed(uid, me, follow, level):
                # 直接删除和这个uid相关的评论
                df = df[df['uid'] != uid]
        except Exception as e:
            print(f"检测{uid}资格时出现错误。\nError message:", str(e))
            df = df[df['uid'] != uid]
        time.sleep(random.uniform(0.5, 2.5))
    return df

if __name__ == "__main__":
    path = 'BV1yXtjeSEDZ_comments.csv'
    df = pd.read_csv(path)
    # 获取不同的uid
    uids = df['uid'].unique()
    # 测试
    df_allowed = extract_allowed_comments(df, 946974)
    df_allowed.to_csv(f'{path}_allowed', index=False)