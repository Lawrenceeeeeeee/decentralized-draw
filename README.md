# 去中心化抽签（Decentralized Draw）

## 项目流程

1. 公钥发布：抽签发起者提前生成 RSA 公私钥，并在公开信道上发布公钥，以确保其无法更改最终结果。
2. 内容提交：参与者通过公开信道发送任意内容。将该内容和参与者的相关信息组合后哈希，并对这些哈希值进行异或累加，生成随机种子。
3. 签名随机种子：发起者将异或累加得到的随机种子作为消息，再次哈希，用私钥进行签名，最后对签名结果进行哈希，得到最终的随机数。
4. 验证随机数：参与者使用已公开的公钥验证签名：
     - 对异或累加的哈希值进行签名验证，确保未被篡改。
     - 验证签名哈希与发起者公开的最终哈希值一致。

整个流程透明、可验证，所有人都为随机数的生成做出了贡献，同时发起者无法舞弊，参与者也无法根据已知信息操控结果，确保随机数生成的公平性与公正性。

## 使用方法：

0. 下载仓库，安装依赖

```
git clone https://github.com/Lawrenceeeeeeee/decentralized-draw.git
cd decentralized-draw
pip install -r requirements.txt
```

1. 发起者运行gen_keys.py生成RSA公私钥，发布公钥，然后输入固定消息运行main.py，生成以下内容

```
消息: example1730342749171066
哈希值: 7a2e27834c756**************************9ffab1b775db41844838
签名 (16进制): 3671aa831e8651d0dc6c584510a****************************************7ac75da4407824a74cec4c556cbad47f2ff0909b3c
```
并且会生成一个包含上述JSON信息的二维码

2. 发布以上内容
3. 用户用verify.py进行验证。将公钥文件放在同目录下，在命令行中传参然后运行

```
python verify.py "固定消息" "生成的哈希值" "生成的签名 (16进制)"
```

## 应用案例

### Bilibili去中心化抽奖

UP主可以在指定视频的评论区中发起抽奖

只是一个示例，您完全可以自定义评论数据的处理方式

由于b站的API的rate limit比较严格，捉摸不透，抽奖资格筛选的用时可能会比较长。如果你的评论区有将近2000多条评论，可能需要一个多小时才能筛选完。所以我将“是否筛选资格”默认设置成了False。如果您有更好的验证资格的方案，欢迎发PR。

#### 使用方法

0. 先获取浏览器的`User-Agent`，打开浏览器，启用开发者模式，在命令行中输入`console.log(navigator.userAgent)`即可获取。然后将`User-Agent`信息填入config.toml中

```
# config.toml
User-Agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
```

1. 按照上文的方法生成RSA公私钥，并公开公钥
2. 运行`bilibili_draw.py`，格式如下（如果选择传csv的话，表格需要包含'timestamp''uid''content'列）

示例：
```
python bilibili_draw.py -bv BV1YJ4m1u7hL 1 
```

```
usage: bilibili_draw.py [-h] [-f FILE] [-bv BV_NUMBER] [-q] [-uid UID] num

Bilibili去中心化抽奖系统

positional arguments:
  num                   抽取个数

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  评论csv文件 (可选，填写后将不进行爬数据和筛选数据)
  -bv BV_NUMBER, --bv_number BV_NUMBER
                        BV号
  -q, --qualification   是否筛选资格（默认不筛选）
  -uid UID, --uid UID   你的uid(检测资格时需要)
```

运行后会生成消息、哈希值和签名（16进制）,以及包含这些信息的二维码（以下简称MHS二维码）

并且会输出中奖的uid

3. 参与者如需验证，可以运行`verify.py`，格式如下

示例：
```
python verify.py -q '/path/to/your/mhs_qr_code_1730791884.png'
```

```
usage: verify.py [-h] [-q QR_CODE] [-m MESSAGE] [-hv HASH_VALUE] [-s SIGNATURE]

验证VRF生成的哈希值和签名

options:
  -h, --help            show this help message and exit
  -q QR_CODE, --qr_code QR_CODE
                        二维码图片路径
  -m MESSAGE, --message MESSAGE
                        活动名+时间戳，作为消息输入
  -hv HASH_VALUE, --hash_value HASH_VALUE
                        生成的哈希值
  -s SIGNATURE, --signature SIGNATURE
                        生成的签名（16进制字符串）
```

输出样例：
```
验证结果: 有效
```