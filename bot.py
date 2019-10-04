from os import path

import nonebot

import config

# 此脚本为入口，所有的相对位置都是以这个脚本为起点
if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'ultbot', 'plugins'),
        'ultbot.plugins'
    )
    nonebot.run()
