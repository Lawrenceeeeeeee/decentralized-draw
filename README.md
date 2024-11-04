# 去中心化抽签（Decentralized Draw）

## 使用方法：

1. 发起者运行gen_keys.py生成公私钥，发布公钥，然后输入固定消息运行main.py，生成以下内容

```
固定消息: example1730342749171066
生成的哈希值: 7a2e27834c756**************************9ffab1b775db41844838
生成的签名 (16进制): 3671aa831e8651d0dc6c584510a****************************************7ac75da4407824a74cec4c556cbad47f2ff0909b3c
```

2. 发布以上内容
3. 用户用verify.py进行验证。将公钥文件放在同目录下，在命令行中传参然后运行

```
python verify.py "固定消息" "生成的哈希值" "生成的签名 (16进制)"
```
