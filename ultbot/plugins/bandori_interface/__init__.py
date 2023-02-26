# 防止在脱离Nonebot时调用此模块报错
if __name__ != "ultbot.plugins.bandori_interface":
    import nonebot

    from .json_crawler import json_crawler

    from nonebot.adapters.onebot.v11 import Event
    from nonebot.adapters.onebot.v11.bot import Bot
    from nonebot.exception import NetworkError
    from nonebot.plugin import on_keyword
    from nonebot.typing import T_State
    from nonebot.adapters.onebot.v11.message import Message

    from .update import new_fetch
    from .data_process import event_process, card_process, gacha_process
    from jieba import posseg
    import jieba
    from nonebot import on_command, permission as perm, require
    from .private_config import user_info, supervisor_id, group_id, bot_id

    scheduler = require('nonebot_plugin_apscheduler').scheduler

    # 在__init__.py使用装饰器才能正常调用
    # 更新时根据日本时间每天14点（大陆时间13点）
    # 每日更新只对新增的json进行更新
    @scheduler.scheduled_job('cron', hour=12, misfire_grace_time=60)
    async def data_daily_update(manual=False):
        bot = nonebot.get_bots()[bot_id]
        # 卡牌更新
        card_details = new_fetch('cards')
        # 活动更新
        event_details = new_fetch('events')
        # 卡池更新
        gacha_details = new_fetch('gacha')

        # 通知管理员
        try:
            await bot.call_api("send_private_msg",
                               user_id=supervisor_id,
                               message=Message('new events ' + str(len(event_details))))
        except NetworkError:
            pass
        # 存在更新则发布更新
        for detail in event_details:
            msg = event_process(detail)
            await bot.call_api("send_private_msg",
                               user_id=supervisor_id,
                               message=Message('本日活动更新：\n' + msg))
            if not manual:
                await bot.call_api("send_group_msg",
                                   group_id=group_id,
                                   message=Message('本日活动更新：\n' + msg))

        # 通知管理员
        try:
            await bot.call_api("send_private_msg",
                               user_id=supervisor_id,
                               message=Message('new cards ' + str(len(card_details))))
        except NetworkError:
            pass
        # 存在更新则发布更新
        for detail in card_details:
            msg = card_process(detail)
            await bot.call_api("send_private_msg",
                               user_id=supervisor_id,
                               message=Message('本日卡牌更新：\n' + msg))
            if not manual:
                await bot.call_api("send_group_msg",
                                   group_id=group_id,
                                   message=Message('本日卡牌更新：\n' + msg))

        # 通知管理员
        try:
            await bot.call_api("send_private_msg",
                               user_id=supervisor_id,
                               message=Message('new gacha ' + str(len(gacha_details))))
        except NetworkError:
            pass
        # 存在更新则发布更新
        for gacha_detail in gacha_details:
            msg, pickup_keys = gacha_process(gacha_detail)
            await bot.call_api("send_private_msg",
                               user_id=supervisor_id,
                               message=Message('本日卡池更新：\n' + msg))
            if not manual:
                await bot.call_api("send_group_msg",
                                   group_id=group_id,
                                   message=Message('本日卡池更新：\n' + msg))
            # PICKUP卡牌信息处理
            for pickup_key in pickup_keys:
                url_path = 'https://bestdori.com/api/cards/'
                card_detail = json_crawler(url_path + pickup_key + '.json', wait_time=1)
                msg = card_process(card_detail)
                await bot.call_api("send_private_msg",
                                   user_id=supervisor_id,
                                   message=Message(msg))
                if not manual:
                    await bot.call_api("send_group_msg",
                                       group_id=group_id,
                                       message=Message(msg))


    fe = on_command("findall_events")


    @fe.handle()
    async def fe_parser(bot: Bot, event: Event, state: T_State):
        stripped_arg = str(event.get_message()).strip()
        stripped_arg_list = list(filter(None, stripped_arg.split(' ')))
        length = len(stripped_arg_list)

        if length == 2:
            state['event_elem'] = stripped_arg_list[0]
            state['detail'] = stripped_arg_list[1].replace("'", "\\'")
        # 参数数目不正确则给出指南
        else:
            await fe.finish('使用指南：\n/findall_events [搜索对象] [匹配字符]'
                            '\n\ne.g.\n/findall_events event_name 小兔子脱逃中！\n\n'
                            '其中有效的[搜索对象]为：\n'
                            'eventName\n'
                            'eventType\n'
                            'attributes\n'
                            'bonus_members\n'
                            'new_rank_four_members\n'
                            'date')
        return


    @fe.got("detail")
    async def findall_events(bot: Bot, event: Event, state: T_State):
        elem = state['event_elem']
        detail = state['detail']


    fc = on_command("findall_cards")


    @fc.handle()
    async def fc_parser(bot: Bot, event: Event, state: T_State):
        stripped_arg = str(event.get_message()).strip()
        stripped_arg_list = list(filter(None, stripped_arg.split(' ')))
        length = len(stripped_arg_list)

        # 首次执行指令
        if length == 2:
            state['card_elem'] = stripped_arg_list[0]
            tmp_string = stripped_arg_list[1]
            # 搜索对象为info时进一步处理
            if state['card_elem'] == 'info':
                tmp_string = tmp_string.split(':')
                if len(tmp_string) != 3 and len(tmp_string) != 4:
                    await fc.finish('有效info参数为[成员ID:属性:稀有度:技能]')
            state['detail'] = tmp_string
        # 参数数目不正确则给出指南
        else:
            await fc.finish('使用指南：\n/findall_cards [搜索对象] [匹配字符]'
                            '\n\ne.g.\n/findall_cards info 1:pure:4:1\n\n'
                            '其中有效的[搜索对象]为：\n'
                            'info [成员ID:属性:稀有度:技能](技能可以省略)\n'
                            'prefix')
        return


    @fc.got("detail")
    async def findall_cards(bot: Bot, event: Event, state: T_State):
        elem = state['card_elem']
        detail = state['detail']


    fg = on_command("findall_gacha")


    @fg.handle()
    async def fg_parser(bot: Bot, event: Event, state: T_State):
        stripped_arg = str(event.get_message()).strip()
        stripped_arg_list = list(filter(None, stripped_arg.split(' ')))
        length = len(stripped_arg_list)

        if length == 2:
            state['gacha_elem'] = stripped_arg_list[0]
            tmp_string = stripped_arg_list[1]
            # 搜索对象为info时进一步处理
            if state['gacha_elem'] == 'info':
                tmp_string = tmp_string.split(':')
                if len(tmp_string) != 1 and len(tmp_string) != 2:
                    await fg.finish('有效info参数为:[时间:类型<special/limited/permanent>]')
            state['detail'] = tmp_string
        # 参数数目不正确则给出指南
        else:
            await fg.finish('使用指南：\n/findall_gacha [搜索对象] [匹配字符]'
                            '\n\ne.g.\n/findall_gacha gachaName Poppin\'Partyガチャ\n\n'
                            '其中有效的[搜索对象]为：\n'
                            'gachaName\n'
                            'info [时间:类型<special/limited/permanent>](类型可以省略)')
        return


    @fg.got("detail")
    async def findall_gacha(bot: Bot, event: Event, state: T_State):
        elem = state['gacha_elem']
        detail = state['detail']


    fi = on_command("find_id")


    @fi.handle()
    async def fi_parser(bot: Bot, event: Event, state: T_State):
        stripped_arg = str(event.get_message()).strip()
        stripped_arg_list = list(filter(None, stripped_arg.split(' ')))
        length = len(stripped_arg_list)

        if length == 2:
            state['elem'] = stripped_arg_list[0]
            state['detail'] = stripped_arg_list[1] + '.json'
        # 参数数目不正确则给出指南
        else:
            await fi.finish('使用指南：\n/find_json [搜索对象] [匹配字符]'
                            '\n\ne.g.\n/find_json events 1\n\n'
                            '其中有效的[搜索对象]为：\n'
                            'events\n'
                            'cards\n'
                            'gacha'
                            )
        return


    @fi.got("detail")
    async def find_json(bot: Bot, event: Event, state: T_State):
        elem = state['elem']
        detail = state['detail']


    nls = on_keyword({'邦邦', 'bang dream', })


    @nls.handle()
    async def natural_language_search(bot: Bot, event: Event, state: T_State):
        # 读取邦邦字典
        jieba.load_userdict('../bandori_data/bd_dict.txt')
        # 确保有效词汇只生效一次
        find_once = True
        event_elem_once = True
        # 活动属性名称dict
        event_dict = {
            'lack_confidence': 'lack_confidence',
            '活动名': 'eventName',
            '活动类型': 'eventType',
            '加成属性': 'attribute',
            '加成成员': 'characters',
            '日期': 'date',
        }
        confidence = 0.0
        stripped_msg = str(event.get_message()).strip().split(' ')
        words = posseg.lcut(stripped_msg[0])
        intent_elem = 'lack_confidence'

        # 计算置信度
        for word in words:
            if word.flag == 'find':
                # 出现'搜索'增加置信度
                if find_once:
                    confidence += 40.0
                    find_once = False
            elif word.flag == 'bbnz':
                # 出现邦邦专名增加置信度
                if event_elem_once:
                    confidence += 40.0
                    event_elem_once = False
                    intent_elem = word.word

        # 执行度大于等于80则进行查找
        if confidence >= 80:
            state['event_elem'] = event_dict[intent_elem]
            state['detail'] = stripped_msg[1].strip().replace("'", "\\'")
            await findall_events(bot, event, state)


    mf = on_command("manual_fetch", permission=perm.SUPERUSER)


    @mf.handle()
    async def manual_fetch(bot: Bot, event: Event):
        try:
            await bot.send(event, 'Processing...')
        except NetworkError:
            pass
        await data_daily_update(manual=True)
        try:
            await bot.send(event, 'Done')
        except NetworkError:
            pass
