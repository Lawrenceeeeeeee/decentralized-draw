import time
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

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
def draw_lottery():
    activity_name = "pre"
    fixed_message = activity_name

    # 加载私钥
    sk = load_private_key()  # 从文件加载私钥

    # 生成VRF结果
    hash_value, signature_hex = vrf_prove(sk, fixed_message)

    # 打印供验证使用的信息
    print("固定消息:", fixed_message)
    print("生成的哈希值:", hash_value)
    print("生成的签名 (16进制):", signature_hex)

# 执行抽签示例
if __name__ == "__main__":
    start = time.time()
    draw_lottery()
    time_lapse = time.time() - start
    print("用时：", time_lapse)