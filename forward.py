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

Wechaty.instance() // Global Instance
    .on('scan', lambda qrcode, status : print('Scan QR Code to login: {}\nhttps://api.qrserver.com/v1/create-qr-code/?data={}'.format(status, encodeURIComponent(qrcode))))
    .on('login', lambda user: print('User {} logined'.format(user)))
    .on('message', lambda message: onMessage(message))
    .start()


