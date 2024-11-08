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

注：项目使用了pyzbar，windows python wheels里是附带zbar dll的，但是其他系统没有，需要自行安装

Mac OS X:

```
brew install zbar
```

Linux:

```
sudo apt-get install libzbar0
```

然后下载仓库，安装python依赖

```
git clone https://github.com/Lawrenceeeeeeee/decentralized-draw.git
cd decentralized-draw
pip install -r requirements.txt
```

1. 抽签发起者运行gen_keys.py生成RSA公私钥，发布公钥，然后运行main.py，输入消息，生成以下内容

```
消息: example1730342749171066
哈希值: 7a2e27834c756**************************9ffab1b775db41844838
签名 (16进制): 3671aa831e8651d0dc6c584510a****************************************7ac75da4407824a74cec4c556cbad47f2ff0909b3c
```

并且会生成一个包含上述JSON信息的二维码

2. 发布以上内容
3. 抽签参与者用verify.py进行验证。将公钥文件（文件名应为 `public_key.pem`）放在同目录下，在命令行中传参然后运行

```
usage: verify.py [-h] [-q QR_CODE] [-m MESSAGE] [-hv HASH_VALUE] [-s SIGNATURE]
```

## 应用案例

### Bilibili去中心化抽奖

UP主可以在指定视频的评论区中发起抽奖

只是一个示例，您完全可以自定义评论数据的处理方式

由于b站的API的rate limit比较严格，捉摸不透，抽奖资格筛选的用时可能会比较长。如果你的评论区有将近2000多条评论，可能需要一个多小时才能筛选完。所以我将“是否筛选资格”默认设置成了False。如果您有更好的验证资格的方案，欢迎发PR。

#### WebUI版本

为了方便大家使用，我写了一个WebUI版本，可以方便地进行抽奖和验证。可以在[这个网站](https://bilidd.cuberlawrence.top)上体验，只是缺少资格验证的功能。

本地运行:

```
python web_app.py
```

#### 使用方法

注意！！！如果你是Mac用户，请一定要给终端或者这个应用开启完全磁盘访问权限，否则无法自动读取cookies

1. 先获取浏览器的 `User-Agent`，打开浏览器，启用开发者模式，在命令行中输入 `console.log(navigator.userAgent)`即可获取。然后将 `User-Agent`信息填入config.toml中

```
# config.toml
User-Agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
```

Windows用户可能无法通过程序提取cookies，建议在 `config.toml`里填写相关cookies项

```
# cookies.toml
# 在浏览器访问`bilibili.com`，打开开发者模式，找到`www.bilibili.com`的cookie，在里面找到下面这几个参数并填写在此处

[cookies]
SESSDATA=""
bili_jct=""
buvid3=""
DedeUserID=""
```

2. 按照上文的方法生成RSA公私钥，并公开公钥
3. 运行 `bilibili_draw.py`，格式如下（如果选择传csv的话，表格需要包含'timestamp''uid''content'列）

示例：

```
python bilibili_draw.py -bv BV1YJ4m1u7hL 1 
```

```
usage: bilibili_draw.py [-h] [-k KEY_PATH] [-f FILE] [-bv BV_NUMBER] [-q] [-uid UID] num

Bilibili去中心化抽奖系统

positional arguments:
  num                   抽取个数

options:
  -h, --help            show this help message and exit
  -k KEY_PATH, --key_path KEY_PATH
                        私钥路径 (默认keys/private_key.pem)
  -f FILE, --file FILE  评论csv文件 (可选，填写后将不进行爬数据和筛选数据)
  -bv BV_NUMBER, --bv_number BV_NUMBER
                        BV号
  -q, --qualification   是否筛选资格（默认不筛选）
  -uid UID, --uid UID   你的uid(检测资格时需要)
```

运行后会生成消息、哈希值和签名（16进制）,以及包含这些信息的二维码（以下简称MHS二维码）

并且会输出中奖的uid

4. 参与者如需验证，可以运行 `verify.py`，格式如下

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

鉴于部分非Windows用户在pyzbar库的安装上会存在问题，这里我提供了一个shell脚本的方案，只需要运行 `run_verify.sh`并按照指示输入即可。

还有Windows的bat版本，运行 `run_verify.bat`即可

不过还是建议各位处理好pyzbar安装问题，可以参考[这篇文章](https://stackoverflow.com/questions/71984213/macbook-m1raise-importerrorunable-to-find-zbar-shared-library-importerror)

示例：

```
$ ./run_verify.sh

请选择验证方式：
1. 二维码验证
2. 手动验证
输入选项 (1 或 2): 1
请输入二维码图像的路径(绝对路径，将图像拖入命令行即可): '/path/to/your/mhs_qr_code.png'
验证结果: 有效
```

```
$ ./run_verify.sh

请选择验证方式：
1. 二维码验证
2. 手动验证
输入选项 (1 或 2): 2
消息: d0ab4c0814c691xxxxxxxxxxxxxxxxxxx6f8dcc9a98d7473dd8336c674190
哈希值: 7536937a1f114xxxxxxxxxxxxxxxxxxxxxxxxxxb34e7ea7c10bb725dd079fb0b
签名: 7b4a7c37a23d193c0xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx1739cf1ea7b7ed
验证结果: 有效
```
