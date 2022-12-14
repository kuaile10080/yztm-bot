from asyncio import events
from nonebot import on_regex,on_command,on_request
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, PrivateMessageEvent, exception

from src.libraries.userenvs import *

import json,random,os,time,re

points_json = {}

def savejson():
    file = open(points_path,"w",encoding='utf-8')
    json.dump(points_json,file)
    file.close()

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
else:
    points_json = {}
    savejson()


#----------匹配大于等于5汉字的消息并概率触发积分----------
regex = '([\u4e00-\u9fa5](.*)){5}'
getpoints = on_regex(regex, priority = 2000, block = False)
@getpoints.handle()
async def _getpoints(bot: Bot, event: GroupMessageEvent):
    print("匹配消息成功：" + str(event.get_message()))
    if random.random() < (points_probability/100):
        qq = str(event.get_user_id())
        if qq not in points_json.keys():
            points_json[qq]={'total':0,'today':0,'update_date':0}
        if points_json[qq]['update_date'] != int(time.strftime('%Y%m%d')):
            points_json[qq]['update_date'] = int(time.strftime('%Y%m%d'))
            points_json[qq]['total'] += 1
            points_json[qq]['today'] = 1
        elif points_json[qq]['today'] < daily_max:
            points_json[qq]['total'] += 1
            points_json[qq]['today'] += 1
        else:
            pass
    savejson()

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
        if points_json[qq]['update_date'] != int(time.strftime('%Y%m%d')):
            temp = 0
        else:
            temp = points_json[qq]['today']
        msg = '您的总积分为：' + str(points_json[qq]['total']) + '\n' + '今天通过群聊获得的积分为：' + str(temp)
        try:
            await querypoint.finish(Message(msg))
        except exception.ActionFailed:
            pass
        except Exception as e:
            print(repr(e))

#----------设置管理者匹配规则----------
async def superuser_checker(bot: Bot, event: Event) -> bool:
    return str(event.get_user_id()) in superusers

#----------管理者查询成员积分----------
querypointsuper = on_command("查成员分",rule = superuser_checker)
@querypointsuper.handle()
async def _querypointsuper(bot: Bot, event: Event):
    msg = str(event.get_message()).split()
    if len(msg)==2:
        try:
            qq = str(int(msg[1]))
        except:
            await querypointsuper.finish(Message("指令格式有误"))
    else:
        await querypointsuper.finish(Message("指令格式有误"))

    if qq not in points_json.keys():
        try:
            await querypointsuper.finish(Message("暂无积分记录"))
        except exception.ActionFailed:
            pass
        except Exception as e:
            print(repr(e))
    else:
        if points_json[qq]['update_date'] != int(time.strftime('%Y%m%d')):
            temp = 0
        else:
            temp = points_json[qq]['today']
        msg = qq + '的总积分为：' + str(points_json[qq]['total']) + '\n' + '今天通过群聊获得的积分为：' + str(temp)
        try:
            await querypointsuper.finish(Message(msg))
        except exception.ActionFailed:
            pass
        except Exception as e:
            print(repr(e))


#----------单群员加减积分----------
single_update = on_command("积分变更", rule = superuser_checker, priority = 10, block = True)
@single_update.handle()
async def _single_update(bot:Bot,event:Event):
    msg = str(event.get_message()).split()
    if len(msg)==3:
        try:
            qq = str(int(msg[1]))
            points = int(msg[2])
        except:
            await single_update.finish(Message("指令格式有误"))
    else:
        await single_update.finish(Message("指令格式有误"))
    if qq in points_json:
        points_json[qq]['total'] += points
        savejson()
    else:
        points_json[qq]={'total':points,'today':0,'update_date':0}
        savejson()
    msg = "群成员" + qq + "的积分"
    if points > 0:
        msg += '+'
    msg += str(points)
    msg += '。\n目前总积分为：'
    msg += str(points_json[qq]['total'])
    await single_update.finish(Message(msg))

#----------全体群员加减积分----------
all_update = on_command("全体积分变更", rule = superuser_checker, priority = 10, block = True)
@all_update.handle()
async def _all_update(bot:Bot,event:GroupMessageEvent):
    msg = str(event.get_message()).split()
    if len(msg)==2:
        try:
            points = int(msg[1])
        except:
            await all_update.finish(Message("指令格式有误"))
    else:
        await all_update.finish(Message("指令格式有误"))
    group = str(re.match("group_(.+)_(.+)",event.get_session_id()).groups()[0])
    data = await bot.call_api('get_group_member_list',**{
        'group_id': group,
        'no_cache': True
    })
    for user in data:
        qq = str(user['user_id'])
        if qq in points_json:
            points_json[qq]['total'] += points
            savejson()
        else:
            points_json[qq]={'total':points,'today':0,'update_date':0}
            savejson()
    await all_update.finish(Message("执行成功"))


#----------管理者导出全体积分列表----------
outputcsv = on_command("导出全体积分列表",aliases={"导出列表","导出全体列表","导出积分列表"},rule = superuser_checker)
@outputcsv.handle()
async def _outputcsv(bot: Bot, event: PrivateMessageEvent):
    content = "qq,总积分\n"
    for qq in points_json:
        content += qq
        content +=","
        content += str(points_json[qq]['total'])
        content += "\n"
    file = open(points_path[:-5] + time.strftime('%m%d%H%M%S') + '_save.csv','w',encoding='gbk')
    file.write(content)
    file.close()
    try:
        await outputcsv.finish(Message("导出成功，请至bot的src/static/目录下查看最新的csv表格文件"))
    except exception.ActionFailed:
        pass
    except Exception as e:
        print(repr(e))

static_path = 'src/static/'
joingroup = on_request()
@joingroup.handle()
async def _joingroup(bot: Bot,event: Event):
    data = eval(event.get_event_description())
    whitellist_path = static_path + str(data['group_id']) + '.txt'
    CDKEY_path = static_path + 'KEY' + str(data['group_id']) + '.txt'
    whitelist = {}
    CDKEYlist = {}
    try:
        file = open(whitellist_path,"r",encoding='utf-8')
        for line in file:
            aline = line.strip().split("=")
            whitelist[aline[0]] = int(aline[1])
        file.close()
        file = open(CDKEY_path,"r",encoding='utf-8')
        for line in file:
            aline = line.strip().split("=")
            CDKEYlist[aline[0]] = int(aline[1])
        file.close()
    except:
        print("白名单与卡密读取失败")
        return
    qq = str(data["user_id"])
    key = data['comment'][-12:]
    if key in CDKEYlist:
        if CDKEYlist[key] == 1:
            keyflag = 1
        else:
            keyflag = 0
    else:
        keyflag = -1
    if qq in whitelist:
        if whitelist[qq] == 1:
            whiteflag = 1
        else:
            whiteflag = 0
    else:
        whiteflag = -1
    
    if keyflag == 1:
        await bot.call_api('set_group_add_request',**{
        'flag': data['flag'],
        'sub_type': 'add',
        'approve': True
        })
        CDKEYlist[key] = 0
        CDKEYliststr = ''
        for key in CDKEYlist:
            CDKEYliststr += key
            CDKEYliststr += "="
            CDKEYliststr += str(CDKEYlist[key])
            CDKEYliststr += "\n"
            file = open(CDKEY_path,"w",encoding='utf-8')
            file.write(CDKEYliststr)
            file.close()
        print(qq + "加群申请已通过卡密方式通过")
    elif whiteflag == 1:
        await bot.call_api('set_group_add_request',**{
        'flag': data['flag'],
        'sub_type': 'add',
        'approve': True
        })
        whitelist[qq] = 0
        whiteliststr = ''
        for qq in whitelist:
            whiteliststr += qq
            whiteliststr += "="
            whiteliststr += str(whitelist[qq])
            whiteliststr += "\n"
            file = open(whitellist_path,"w",encoding='utf-8')
            file.write(whiteliststr)
            file.close()
        print(qq + "加群申请已通过白名单方式通过")
    else:
        await bot.call_api('set_group_add_request',**{
        'flag': data['flag'],
        'sub_type': 'add',
        'approve': False
        })
        print(qq + "卡密错误且不在白名单，已拒绝")

    




