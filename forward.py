#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
import itchat
import time
from itchat.content import *
import yaml
from telegram_util import matchKey, log_on_fail

def getFile(name):
	with open(name) as f:
		return yaml.load(f, Loader=yaml.FullLoader)

bot = Updater(getFile('credential')['bot_token'], use_context=True).bot
debug_group = bot.get_chat(-1001198682178)
channel = bot.get_chat('@web_record')
link_status = {}

@log_on_fail(debug_group)
def text_reply_imp(msg):
	if not msg.Url:
		return
	link_status[msg.FileName] = link_status.get(msg.FileName, 0)
	if link_status.get[msg.FileName] >= 1:
		return # sent before
	if matchKey(msg.User.NickName, ['女权', '平权', 'hardcore', 'dykes']):
		link_status[msg.FileName] += 1
	else:
		link_status[msg.FileName] += 0.5
	if link_status[msg.FileName] >= 1:
		channel.send_message(msg.Url)

@itchat.msg_register(SHARING, isGroupChat=True)
def text_reply(msg):
	text_reply_imp(msg)

@itchat.msg_register(TEXT, isFriendChat=True)
def text_reply(msg):
	debug_group.send_message('%s send wechat message: %s' % (msg.User.NickName, msg.text))

itchat.auto_login(enableCmdQR=2, hotReload=True)
itchat.run(True)