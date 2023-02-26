import asyncio
import time
from datetime import datetime
from datetime import timedelta
import json
import pathlib
import os
import re
import pytz
from nonebot.adapters.onebot.v11 import Event, Message, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.plugin import on_message
from nonebot.rule import regex
from nonebot.typing import T_State
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
import prettytable
from PIL import Image, ImageDraw, ImageFont
from nonebot import on_command, on_keyword


go_cqhttp_path = "W:\Program Files\go-http"


def get_shadow_root(driver: WebDriver) -> WebElement:
    WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.TAG_NAME, "gradio-app"))
    )

    return driver.execute_script("return document.querySelector('gradio-app').shadowRoot")


tip = on_command("draw")


@tip.handle()
async def draw(bot: Bot, event: Event):
    raw_command_lines = str(event.get_message()).strip()

    # 删除换行符
    command_lines_without_newline = raw_command_lines.replace("\r\n", "")

    command_lines = list(filter(None, command_lines_without_newline.split(' ', 1)))

    if len(command_lines) == 1:
        await bot.send(event, '格式：/draw p:"此处填写描述" np:"此处填写否定描述" \n'
                              '样例：/draw [p:"masterpiece, best quality"] [np:"bad hands, text"] [img:"[图片]"]')
        return

    await bot.send(event, message="生成图片需要一定的时间，请稍后")

    prompts_match = re.search(r"p:\"(.*?)\"", command_lines[1])
    negative_prompts_match = re.search(r"np:\"(.*?)\"", command_lines[1])
    img_match = re.search(r"img:\"\[CQ:image,file=(.*?.image).*]\"", command_lines[1])

    chrome_options = Options()
    chrome_options.binary_location = "./tools/chromium/chrome.exe"
    chrome_service = Service("./tools/chromedriver")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    url = 'http://127.0.0.1:7860/'
    chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    chrome_driver.get(url)

    shadow_root = get_shadow_root(chrome_driver)

    if img_match is not None:
        img2img_button = shadow_root.find_element(By.ID, "tabs").find_elements(By.TAG_NAME, "div")[0]. \
            find_elements(By.TAG_NAME, "button")[1]
        img2img_button.click()

        img = await bot.get_image(file=img_match.group(1))

        img_input = shadow_root.find_element(By.ID, "img2img_image").find_element(
            By.CSS_SELECTOR, "input[accept='image/x-png,image/gif,image/jpeg']"
        )

        # 提交图片
        img_input.send_keys(os.path.join(go_cqhttp_path, img["file"]))

        if prompts_match is not None:
            prompt_input = shadow_root.find_element(By.ID, "img2img_prompt").find_element(
                By.CSS_SELECTOR, "textarea[placeholder='Prompt (press Ctrl+Enter or Alt+Enter to generate)']"
            )
            prompt_input.send_keys(prompts_match.group(1))

        if negative_prompts_match is not None:
            negative_prompt_input = shadow_root.find_element(By.ID, "img2img_neg_prompt").find_element(
                By.CSS_SELECTOR, "textarea[placeholder='Negative prompt (press Ctrl+Enter or Alt+Enter to generate)']",
            )
            negative_prompt_input.send_keys(negative_prompts_match.group(1))

        generate_button = shadow_root.find_element(By.ID, "img2img_generate")
    else:
        if prompts_match is not None:
            prompt_input = shadow_root.find_element(By.ID, "txt2img_prompt").find_element(
                By.CSS_SELECTOR, "textarea[placeholder='Prompt (press Ctrl+Enter or Alt+Enter to generate)']"
            )
            prompt_input.send_keys(prompts_match.group(1))

        if negative_prompts_match is not None:
            negative_prompt_input = shadow_root.find_element(By.ID, "txt2img_neg_prompt").find_element(
                By.CSS_SELECTOR, "textarea[placeholder='Negative prompt (press Ctrl+Enter or Alt+Enter to generate)']",
            )
            negative_prompt_input.send_keys(negative_prompts_match.group(1))

        generate_button = shadow_root.find_element(By.ID, "txt2img_generate")

    generate_button.click()

    img = WebDriverWait(chrome_driver, 30).until(
        lambda driver: shadow_root.find_element(
            By.CSS_SELECTOR,
            "img[class='h-full w-full overflow-hidden object-contain']"
        )
    )

    # 发送图片
    withdraw_timer = 20
    message = Message('为确保合法合规，此消息只会保存{0}s[CQ:image,file={1}]'.format(withdraw_timer, img.get_attribute("src")))

    if type(event) == PrivateMessageEvent:
        send_result = await bot.send_msg(user_id=int(event.user_id),
                                         message=message)
    else:
        send_result = await bot.send_msg(group_id=int(event.group_id),
                                         message=message)

    chrome_driver.quit()

    await sleep_delete(bot, send_result["message_id"], withdraw_timer)


async def sleep_delete(bot: Bot, message_id, timer):
    await asyncio.sleep(timer)
    await bot.delete_msg(message_id=message_id)
