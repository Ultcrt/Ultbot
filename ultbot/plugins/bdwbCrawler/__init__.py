import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from .htmlProcess import crawler, get_event_url
from .privateConfig import weibo_cookie, user_info
from .dataProcess import data_process
from .write_to_db import write_to_db
from nonebot import on_command, CommandSession, permission as perm


@nonebot.scheduler.scheduled_job('cron', day_of_week='tue', hour=15)
async def bdwb_crawler():
    # 邦邦微博主页储存在tmp_root，活动详情储存在tmp_detail
    tmp_root = 'tmp_root.html'
    tmp_detail = 'tmp_detail.html'
    root_url = 'https://weibo.cn/u/6314659177'

    # 爬取主页
    crawler(root_url, weibo_cookie, tmp_root)
    # 获取活动详情页url
    detail_url = get_event_url(tmp_root)
    # 爬取活动详情页，爬取失败返回None
    if detail_url is None:
        raise ValueError
    else:
        crawler(detail_url, weibo_cookie, tmp_detail)

    # 获取活动信息
    event_info = data_process(tmp_detail)

    # 写入数据库
    write_to_db(event_info, user_info)

    # 转发活动信息
    bot = nonebot.get_bot()
    bonus_members_lined = event_info[3].replace(';', '\n')
    new_rank_four_lined = event_info[4].replace(';', '\n')
    try:
        await bot.send_group_msg(group_id=912732378,
                                 message='本周邦邦活动：\n%s\n\n'
                                         '活动类型：\n%s\n\n'
                                         '加成属性：\n%s\n\n'
                                         '加成成员：\n%s\n'
                                         '新增★4成员：\n%s\n'
                                         '持续时间：\n%s\n'
                                         '至\n%s' % (event_info[0], event_info[1], event_info[2], bonus_members_lined,
                                                    new_rank_four_lined, event_info[5], event_info[6],))
    except CQHttpError:
        pass


@on_command('test', only_to_me=False, permission=perm.SUPERUSER)
async def _(session: CommandSession):
    await bdwb_crawler()
    try:
        await session.send('Done.')
    except CQHttpError:
        pass
