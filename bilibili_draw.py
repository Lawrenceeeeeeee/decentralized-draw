import pandas as pd
import time
import random
import argparse
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from src import get_user_info as gui
from src import get_comments as gc
from src import allowed_users as au


parser = argparse.ArgumentParser(description="Bilibili去中心化抽奖系统")
    
parser.add_argument("num", type=int, help="抽取个数")
parser.add_argument("-f", "--file", type=str, help="评论csv文件 (可选，填写后将不进行爬数据和筛选数据)")
parser.add_argument("-bv", "--bv_number", type=str, help="BV号")
parser.add_argument("-q", "--qualification", action="store_true", default=False, help="是否筛选资格（默认不筛选）")
parser.add_argument("-uid", "--uid", type=int, help="你的uid(检测资格时需要)")

# 解析参数
args = parser.parse_args()

# 抽取个数
num = args.num

if args.file:
    df = pd.read_csv(args.file)
else:
    if not args.bv_number:
        raise ValueError("请提供BV号")
    # 视频BV号
    bv = args.bv_number
    start = time.time()
    print(f'开始获取{bv}的评论')
    df = gc.get_full_comments('1', bv)
    df.to_csv(f'{bv}_comments.csv', header=True, encoding='utf-8')
    # df = pd.read_csv('BV1yXtjeSEDZ_comments.csv')
    time_lapse = time.time() - start
    print(f'用时：{time_lapse}')

    # df = pd.read_csv('BV1YJ4m1u7hL_comments.csv')
    if args.qualification:
        if not args.uid:
            raise ValueError("请提供你的uid")
        start = time.time()
        print(f'开始提取{bv}的允许抽奖评论')
        df = au.extract_allowed_comments(df, args.uid)
        df.to_csv(f'{bv}_allowed.csv', index=False, encoding='utf-8')
        time_lapse = time.time() - start
        print(f'用时：{time_lapse}')

# 获取不同的uid
uids = df['uid'].unique()

# 从文件加载私钥
def load_private_key(sk_filename="private_key.pem"):
    with open(sk_filename, "rb") as sk_file:
        sk = RSA.import_key(sk_file.read())
    return sk

# VRF生成函数
def vrf_prove(sk, message):
    # 使用RSA签名
    message_bytes = message.encode()
    message_hash = SHA256.new(message_bytes)  # 使用Crypto.Hash.SHA256生成哈希
    signature = pkcs1_15.new(sk).sign(message_hash)
    hash_value = SHA256.new(signature).hexdigest()  # 将签名进行二次哈希
    # 将签名转换为16进制字符串，便于传输
    signature_hex = signature.hex()
    return hash_value, signature_hex



# 抽签示例
def draw_lottery(me: int = None):
    # 遍历所有uid，获取对应评论的时间戳和评论，然后组合成"uid+时间戳+评论"，hash后进行异或累加
    message_accumulate_hash = 0
    for uid in uids:
        
        df_uid = df[df['uid'] == uid]
        # print(df_uid)
        fixed_message = str(uid)
        if not df_uid.empty:
            first_comment = df_uid.iloc[0]
            fixed_message += str(first_comment['timestamp']) + first_comment['content']
        # print(fixed_message)
        
        hashed_message = SHA256.new(fixed_message.encode()).hexdigest()
        message_accumulate_hash ^= int(hashed_message, 16)
        
        activity_name = hex(message_accumulate_hash)[2:]
    fixed_message = activity_name

    # 加载私钥
    sk = load_private_key()  # 从文件加载私钥

    # 生成VRF结果
    hash_value, signature_hex = vrf_prove(sk, fixed_message)

    # 打印供验证使用的信息
    print("固定消息:", fixed_message)
    print("生成的哈希值:", hash_value)
    print("生成的签名 (16进制):", signature_hex)
    
    random.seed(int(hash_value, 16))
    winner = random.sample(list(uids),num)
    print("中奖者:", winner)

# 执行抽签示例
if __name__ == "__main__":
    draw_lottery()