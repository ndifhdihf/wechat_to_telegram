#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater

from wechaty import Wechaty

Wechaty.instance() // Global Instance
  .on('scan', lambda qrcode, status : print('Scan QR Code to login: {}\nhttps://api.qrserver.com/v1/create-qr-code/?data={}'.format(status, encodeURIComponent(qrcode))))
  .on('login', lambda user: print('User {} logined'.format(user)))
  .on('message', lambda message: print('Message: {}'.format(message)))
  .start()

def getFile(name):
    with open(name) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

credential = getFile('credential')

bot = Updater(credential['bot_token'], use_context=True).bot
debug_group = bot.get_chat(-1001198682178)
