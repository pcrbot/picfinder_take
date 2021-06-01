import re

from asyncio import sleep
from datetime import datetime,timedelta

from nonebot import get_bot

from hoshino import Service, log, priv, aiorequests
from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import DailyNumberLimiter
from hoshino.config import NICKNAME

from .image import get_image_data_sauce, get_image_data_ascii, check_screenshot
from .config import threshold, SAUCENAO_KEY, SEARCH_TIMEOUT, CHAIN_REPLY, DAILY_LIMIT, helptext, CHECK

if type(NICKNAME)!=list:
    NICKNAME=[NICKNAME]

sv = Service('picfinder', help_=helptext)

lmtd = DailyNumberLimiter(DAILY_LIMIT)
logger = log.new_logger('image')

class PicListener:
    def __init__(self):
        self.on = {}
        self.count = {}
        self.timeout = {}

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def turn_on(self, gid, uid):
        self.on[gid] = uid
        self.timeout[gid] = datetime.now()+timedelta(seconds=SEARCH_TIMEOUT)
        self.count[gid] = 0

    def turn_off(self, gid):
        self.on[gid] = None
        self.count[gid] = None
        self.timeout[gid] = None

    def count_plus(self, gid):
        self.count[gid] += 1

pls=PicListener()

@sv.on_prefix(('识图','搜图','查图','找图'), only_to_me=True)
async def start_finder(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    mid= ev.message_id
    ret = re.search(r"\[CQ:image,file=(.*),url=(.*)\]", str(ev.message))
    if not ret:
        if pls.get_on_off_status(gid):
            if uid == pls.on[gid]:
                await bot.finish(ev, f"您已经在搜图模式下啦！\n如想退出搜图模式请发送“谢谢竹竹”~")
            else:
                await bot.finish(ev, f"本群[CQ:at,qq={pls.on[gid]}]正在搜图，请耐心等待~")
        pls.turn_on(gid, uid)
        await bot.send(ev, f"了解～请发送图片吧！支持批量噢！\n如想退出搜索模式请发送“谢谢{NICKNAME[0]}”")
        await sleep(30)
        ct = 0
        while pls.get_on_off_status(gid):
            if datetime.now() < pls.timeout[gid] and ct<10:
                await sleep(30)
                if ct != pls.count[gid]:
                    ct = pls.count[gid]
                    pls.timeout[gid] = datetime.now()+timedelta(seconds=30)
            else:
                pls.turn_off(ev.group_id)
                await bot.send(ev, f"由于超时，已为您自动退出搜图模式，以后要记得说“谢谢{NICKNAME[0]}”来退出搜图模式噢~")
                return
    if not priv.check_priv(ev, priv.SUPERUSER):
        if not lmtd.check(uid):
            await bot.send(ev, f'您今天已经搜过{DAILY_LIMIT}次图了，休息一下明天再来吧~', at_sender=True)
            return
    file= ret.group(1)
    image_data = ret.group(2)
    if CHECK:
        result = await check_screenshot(bot, file, image_data)
        if result:
            if result==1:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是手机截屏，请进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            if result==2:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是长图拼接，请进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            return
    await bot.send(ev, '正在搜索，请稍候～')
    await picfinder(bot, ev, image_data)

@sv.on_message('group')
async def picmessage(bot, ev: CQEvent):
    mid= ev.message_id
    ret = re.search(r"\[CQ:at,qq=(\d*)\]", str(ev.message))
    atcheck = False
    batchcheck = False
    if ret:
        if int(ret.group(1)) == int(ev.self_id):
            atcheck = True
    if pls.get_on_off_status(ev.group_id):
        if int(pls.on[ev.group_id]) == int(ev.user_id):
            batchcheck = True
    if not(batchcheck or atcheck):
        return
    uid = ev.user_id
    ret = re.search(r"\[CQ:image,file=(.*)?,url=(.*)\]", str(ev.message))
    if not ret:
        return
    file= ret.group(1)
    url = ret.group(2)
    if CHECK:
        result = await check_screenshot(bot, file, url)
        if result:
            if result==1:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是手机截屏，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            if result==2:
                await bot.send(ev, f'[CQ:reply,id={mid}]该图似乎是长图拼接，请手动进行适当裁剪后再尝试搜图~\n*请注意搜索漫画时务必截取一个完整单页进行搜图~')
            return
    if not priv.check_priv(ev, priv.SUPERUSER):
        if not lmtd.check(uid):
            await bot.send(ev, f'您今天已经搜过{DAILY_LIMIT}次图了，休息一下明天再来吧～', at_sender=True)
            if pls.get_on_off_status(ev.group_id):
                pls.turn_off(ev.group_id)
                return
    if pls.get_on_off_status(ev.group_id):
        pls.count_plus(ev.group_id)

    await bot.send(ev, '正在搜索，请稍候～')
    await picfinder(bot, ev, url)


@sv.on_prefix('谢谢')
async def thanks(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    if name not in NICKNAME:
        return
    if pls.get_on_off_status(ev.group_id):
        if pls.on[ev.group_id]!=ev.user_id:
            await bot.send(ev, '不能替别人结束搜图哦～')
            return
        pls.turn_off(ev.group_id)
        await bot.send(ev, '不用谢～')
        return
    await bot.send(ev, 'にゃ～')

async def chain_reply(bot, ev, chain, msg):
    if not CHAIN_REPLY:
        await bot.send(ev, msg)
        return chain
    else:
        data ={
                "type": "node",
                "data": {
                    "name": str(NICKNAME[0]),
                    "uin": str(ev.self_id),
                    "content": str(msg)
                        }
            }
        chain.append(data)
        return chain

async def picfinder(bot, ev, image_data):
    uid = ev.user_id
    chain=[]
    result = await get_image_data_sauce(image_data, SAUCENAO_KEY)
    image_data_report=result[0]
    simimax=result[1]
    if 'Index #' in image_data_report:
        await bot.send_private_msg(self_id=ev.self_id, user_id=bot.config.SUPERUSERS[0], message='发生index解析错误')
        await bot.send_private_msg(self_id=ev.self_id, user_id=bot.config.SUPERUSERS[0], message=image_data)
        await bot.send_private_msg(self_id=ev.self_id, user_id=bot.config.SUPERUSERS[0], message=image_data_report)
    chain = await chain_reply(bot, ev, chain, image_data_report)

    if float(simimax) > float(threshold):
        lmtd.increase(uid)
    else:
        if simimax != 0:
            chain = await chain_reply(bot, ev, chain, "相似度过低，换用ascii2d检索中…")
        else:
            logger.error("SauceNao not found imageInfo")
            chain = await chain_reply(bot, ev, chain, 'SauceNao检索失败,换用ascii2d检索中…')

        image_data_report = await get_image_data_ascii(image_data)
        if image_data_report[0]:
            chain = await chain_reply(bot, ev, chain, image_data_report[0])
            lmtd.increase(uid)
        if image_data_report[1]:
            chain = await chain_reply(bot, ev, chain, image_data_report[1])
        if not (image_data_report[0] or image_data_report[1]):
            logger.error("ascii2d not found imageInfo")
            chain = await chain_reply(bot, ev, chain, 'ascii2d检索失败…')
        
    if CHAIN_REPLY:
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=chain)

bot=get_bot()

@bot.on_message('private')
async def picprivite(ctx):
    type=ctx["sub_type"]
    sid=int(ctx["self_id"])
    uid=int(ctx["sender"]["user_id"])
    gid=0
    ret = re.match(r"\[CQ:image,file=.*?,url=(.*?)\]", str(ctx['message']))
    if not ret:
        if '搜图' in str(ctx['message']) or '搜图' in str(ctx['message']) or '查图' in str(ctx['message']) or '找图' in str(ctx['message']):
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=f'私聊搜图请直接发送图片~')
        return
    if not lmtd.check(uid):
        await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=f'您今天已经搜过{DAILY_LIMIT}次图了，休息一下明天再来吧~')
        return
    if type == "group":
        gid=int(ctx["sender"]["group_id"])
        await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message='临时会话含图片与网址消息极大概率被吞，如搜图结果无法显示请换用群聊搜索或添加bot好友~')
    url=ret.group(1)
    await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message='正在搜索，请稍候～')
    result = await get_image_data_sauce(url, SAUCENAO_KEY)
    image_data_report=result[0]
    simimax=result[1]
    if 'Index #' in image_data_report:
        await bot.send_private_msg(self_id=sid, user_id=bot.config.SUPERUSERS[0], message='发生index解析错误')
        await bot.send_private_msg(self_id=sid, user_id=bot.config.SUPERUSERS[0], message=url)
        await bot.send_private_msg(self_id=sid, user_id=bot.config.SUPERUSERS[0], message=image_data_report)
    await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=image_data_report)

    if float(simimax) > float(threshold):
        lmtd.increase(uid)
    else:
        if simimax != 0:
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message="相似度过低，换用ascii2d检索中…")
        else:
            logger.error("SauceNao not found imageInfo")
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message='SauceNao检索失败,换用ascii2d检索中…')

        image_data_report = await get_image_data_ascii(url)
        if image_data_report[0]:
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=image_data_report[0])
            lmtd.increase(uid)
        if image_data_report[1]:
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message=image_data_report[1])
        if not (image_data_report[0] or image_data_report[1]):
            logger.error("ascii2d not found imageInfo")
            await bot.send_msg(self_id=sid, user_id=uid, group_id=gid, message='ascii2d检索失败…')
