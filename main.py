import time
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import qrcode
from PIL import Image
import json

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
def draw_lottery(message=""):
    # 加载私钥
    sk = load_private_key()  # 从文件加载私钥

    # 生成VRF结果
    hash_value, signature_hex = vrf_prove(sk, message)

    # 打印供验证使用的信息
    print("消息:", message)
    print("哈希值:", hash_value)
    print("签名:", signature_hex)
    
    data_dict = {
        "message": message,
        "hash_value": hash_value,
        "signature": signature_hex
    }
    
    data_json = json.dumps(data_dict, ensure_ascii=False, indent=2)
    
    # 生成MHS二维码
    qr = qrcode.make(data_json)
    qr_path = f"mhs_qr_code_{int(time.time())}.png"
    qr.save(qr_path)
    print(f"二维码已保存为 {qr_path}")

# 执行抽签示例
if __name__ == "__main__":
    start = time.time()
    draw_lottery("test")
    time_lapse = time.time() - start
    print("用时：", time_lapse)