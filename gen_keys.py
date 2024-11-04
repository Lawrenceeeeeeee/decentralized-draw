from Crypto.PublicKey import RSA

# 保存私钥和公钥的函数
def save_keys(sk, vk, sk_filename="private_key.pem", vk_filename="public_key.pem"):
    with open(sk_filename, "wb") as sk_file:
        sk_file.write(sk.export_key(format="PEM"))  # 保存私钥
    with open(vk_filename, "wb") as vk_file:
        vk_file.write(vk.export_key(format="PEM"))  # 保存公钥

# 生成RSA密钥对并保存
def generate_and_save_keys():
    sk = RSA.generate(2048)  # 生成2048位的RSA私钥
    vk = sk.publickey()  # 生成对应的公钥
    save_keys(sk, vk)
    print("RSA密钥已生成并保存到文件中")

# 执行生成密钥
if __name__ == "__main__":
    generate_and_save_keys()