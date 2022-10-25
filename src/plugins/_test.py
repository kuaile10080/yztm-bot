from nonebot import on_regex,on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent, exception
import time

test1 = on_command('sleepandreply')
@test1.handle()
async def _test1(bot:Bot,event:GroupMessageEvent):
    time.sleep(10)
    await test1.finish(Message("reply!"))

test2 = on_command('imm')
@test2.handle()
async def _test2(bot:Bot,event:GroupMessageEvent):
    await test2.finish(Message("2!"))