#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
import itchat
import time
from itchat.content import *
import yaml
from telegram_util import matchKey

def getFile(name):
	with open(name) as f:
		return yaml.load(f, Loader=yaml.FullLoader)

bot = Updater(getFile('credential')['bot_token'], use_context=True).bot
debug_group = bot.get_chat(-1001198682178)
channel = bot.get_chat('@web_record')

@itchat.msg_register(SHARING, isGroupChat=True)
def text_reply(msg):
	if not matchKey(msg.User.NickName, ['女权', '平权', 'hardcore', 'dykes']):
		return
	channel.send_message(msg.Url)

@itchat.msg_register(TEXT, isFriendChat=True)
def text_reply(msg):
	debug_group.send_message('%s send wechat message: %s' % (msg.User.NickName, msg.text))

itchat.auto_login(enableCmdQR=True, hotReload=True)
itchat.run(True)