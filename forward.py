#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
from wechaty import Wechaty

def getFile(name):
    with open(name) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

bot = Updater(getFile('credential')['bot_token'], use_context=True).bot
debug_group = bot.get_chat(-1001198682178)
channel = bot.get_chat('@web_record')

def onMessage(message):
    print(message)

Wechaty.instance()
    .on('scan', lambda qrcode, status : print(qrcode))
    .on('login', lambda user: print('User {} logined'.format(user)))
    .on('message', onMessage
    .start()


