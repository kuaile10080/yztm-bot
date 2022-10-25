# 积分bot 使用指南

## Step 0. 一些说明

管理者列表，触发概率，每日上限：
用记事本打开src\libraries\userenvs.py
按照格式修改


积分信息以json格式保存在src\static\points.json
没有保存每个成员属于哪个群。因此如果有人同时在多个，那么他的每天在所有群获得的积分加起来不超过设置的积分上限。


**指令说明**
群成员 发言时消息里包括至少5个汉字就会触发程序按概率加积分
（仅限群聊）


群成员 私聊发送 “查询积分” 或 “查分” 或 “积分” 可以查询到总积分与当天通过群聊获得的积分
（仅限私聊）


管理者 发送“查成员分 QQ号”可以查询某个成员的积分 如 “查成员分 123456789”
管理者 发送“积分变更 QQ号 积分”可以变更某人的积分 如 “积分变更 123456789 -20”
（这2条指令既可以私聊用也可以在群聊里用。如果私聊用，并且跟bot没有加好友的话，控制台会报错，但是不影响使用）


管理者 发送“全体积分变更 积分”可以变更该群全体成员的积分 如 “全体积分变更 100”
（仅限群聊）





## Step 1. 下面是抄的部署教程

建议使用conda安装环境

```
conda create --name JIFENBOT python=3.9
conda activate JIFENBOT
```

## Step 2. 运行项目

**您需要打开控制台，并切换到该项目所在的目录。**

在打开的控制台中输入
```
python --version
```
控制台应该会打印出 Python 的版本。如果提示找不到 `python` 命令，请检查环境变量或重装 Python，**并务必勾选 Add Python to system PATH**。

之后，输入
```
pip install -r requirements.txt
```
安装依赖完成后，运行
```
python bot.py
```
运行项目。如果输出如下所示的内容，代表运行成功：
```
10-26 05:17:50 [SUCCESS] nonebot | NoneBot is initializing...
10-26 05:17:50 [INFO] nonebot | Current Env: prod
10-26 05:17:50 [SUCCESS] nonebot | Succeeded to import "public"
10-26 05:17:50 [SUCCESS] nonebot | Running NoneBot...
10-26 05:17:50 [INFO] uvicorn | Started server process [18564]
10-26 05:17:50 [INFO] uvicorn | Waiting for application startup.
10-26 05:17:50 [INFO] uvicorn | Application startup complete.
10-26 05:17:50 [INFO] uvicorn | Uvicorn running on http://0.0.0.0:11219 (Press CTRL+C to quit)
```
**运行成功后请勿关闭此窗口，后续需要与 CQ-HTTP 连接。**

## Step 3. 连接 CQ-HTTP

前往 https://github.com/Mrs4s/go-cqhttp > Releases，下载适合自己操作系统的可执行文件。
go-cqhttp 在初次启动时会询问代理方式，选择反向 websocket 代理即可。

之后用任何文本编辑器打开`config.yml`文件，设置反向 ws 地址、上报方式：
```yml
message:
  post-format: array
  
servers:
  - ws-reverse:
      universal: ws://127.0.0.1:11219/onebot/v11/ws
```

需要通过非好友临时会话查询积分的话，需要更改以下设置为true
```yml
# 是否允许发送临时会话消息
allow-temp-session: true
```
有人说临时会话会使账号更容易被腾讯风控。我试了一会儿暂时没有发现问题。

然后设置您的 QQ 号和密码。您也可以不设置密码，选择扫码登陆的方式。

登陆成功后，后台应该会发送一条类似的信息：
```
08-02 11:50:51 [INFO] nonebot | WebSocket Connection from CQHTTP Bot [QQ号] Accepted!
```
至此，您可以和对应的 QQ 号聊天并使用 积分bot 的所有功能了。

## License

MIT

您可以自由使用本项目的代码用于商业或非商业的用途，但必须附带 MIT 授权协议。
