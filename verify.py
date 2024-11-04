import random
import argparse
from hashlib import sha256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# 从文件加载公钥的函数
def load_public_key(vk_filename="public_key.pem"):
    with open(vk_filename, "rb") as vk_file:
        vk = RSA.import_key(vk_file.read())
    return vk

# 验证VRF生成的哈希值和签名
def verify_vrf(vk, message, hash_value, signature):
    # 使用公钥验证签名的有效性
    message_bytes = message.encode()
    message_hash = SHA256.new(message_bytes)
    
    try:
        pkcs1_15.new(vk).verify(message_hash, signature)
        computed_hash = sha256(signature).hexdigest()
        return computed_hash == hash_value
    except (ValueError, TypeError):
        return False

# 用户验证和结果重现示例
def user_verification_example(fixed_message, provided_hash_value, provided_signature):
    # 加载公钥并验证
    vk = load_public_key()
    is_valid = verify_vrf(vk, fixed_message, provided_hash_value, provided_signature)
    
    if is_valid:
        print("验证结果: 有效")
        
        # 使用哈希值重现随机种子
        seed_value = int(provided_hash_value, 16)
        random.seed(seed_value)
    else:
        print("验证结果: 无效")

# 命令行解析
def main():
    parser = argparse.ArgumentParser(description="验证VRF生成的哈希值和签名")
    parser.add_argument("message", help="活动名+时间戳，作为消息输入")
    parser.add_argument("hash_value", help="生成的哈希值")
    parser.add_argument("signature", help="生成的签名（16进制字符串）")

    args = parser.parse_args()

    # 将签名转换为字节格式
    provided_signature = bytes.fromhex(args.signature)
    
    # 执行验证
    user_verification_example(args.message, args.hash_value, provided_signature)

if __name__ == "__main__":
    main()