from msilib.schema import Upgrade
from nonebot import on_regex,on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent, exception

from src.libraries.userenvs import *

import json,random,os,time

# data = Bot.call_api('get_group_info',**{
#     'group_id': 474624734
# })
#----------加载积分文件----------
points_path = 'src/static/points.json'
if os.path.exists(points_path):
    file = open(points_path,"r",encoding='utf-8')
    try:
        points_json = json.load(file)
        file.close()
    except:
        file.seek(0)
        filebkp = open(points_path[:-5] + str(time.time()) + '_bkp.json','w',encoding='utf-8')
        filebkp.write(file.read())
        file.close()
        filebkp.close()
        points_json = {}
else:
    points_json = {}
    file = open(points_path,"w",encoding='utf-8')
    json.dump(points_json,file)
    file.close()


#----------匹配大于等于5汉字的消息并概率触发积分----------
regex = '([\u4e00-\u9fa5](.*)){5}'
getpoints = on_regex(regex, priority = 200, block = False)
@getpoints.handle()
async def _getpoints(bot: Bot, event: GroupMessageEvent):
    print("匹配消息成功：" + str(event.get_message()))
    if random.random() < (points_probability/100):
        qq = str(event.get_user_id())
        if qq not in points_json.keys():
            points_json[qq]={'total':0,'today':0,'upgrade':0}
        if points_json[qq]['upgrade'] != int(time.strftime('%Y%m%d')):
            points_json[qq]['upgrade'] = int(time.strftime('%Y%m%d'))
            points_json[qq]['total'] += 1
            points_json[qq]['today'] = 1
        elif points_json[qq]['today'] < daily_max:
            points_json[qq]['total'] += 1
            points_json[qq]['today'] += 1
        else:
            pass
    file = open(points_path,"w",encoding='utf-8')
    json.dump(points_json,file)
    file.close()

#----------私聊查询积分----------
querypoint = on_command("查询积分", aliases={"查分","积分"})
@querypoint.handle()
async def _querypoint(bot: Bot, event: PrivateMessageEvent):
    qq = str(event.get_user_id())
    if qq not in points_json.keys():
        try:
            await querypoint.finish(Message("暂无积分记录，请在群内积极发言"))
        except exception.ActionFailed:
            pass
        except Exception as e:
            print(repr(e))
    else:
        if points_json[qq]['upgrade'] != int(time.strftime('%Y%m%d')):
            temp = 0
        else:
            temp = points_json[qq]['today']
        msg = '您至今天的总积分为：' + str(points_json[qq]['total']) + '\n' + '您今天获得的积分为：' + str(points_json[qq]['today'])
        try:
            await querypoint.finish(Message(msg))
        except exception.ActionFailed:
            pass
        except Exception as e:
            print(repr(e))