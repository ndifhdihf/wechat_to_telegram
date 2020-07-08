#!/usr/bin/env python
# -*- coding: utf-8 -*-

BLACKLIST = ['waerrpage', 'MzIwOTkzNzQ0MQ', 'Panziye4869', 'Artemis', 
	'support.weixin.qq.com', 'volition', 'MzI5NzUxMDU4OQ', '/promo/', 
	'MzI0ODg4NDM5Mw', 'MzAwNjgzMTQ5NQ', 'MzIyOTQyNDY2OQ']

from telegram.ext import Updater
import itchat
from itchat.content import *
from telegram_util import matchKey, log_on_fail
from common import getFile
from export_to_telegraph import getTitle
import os
import plain_db

bot = Updater(getFile('credential')['bot_token'], use_context=True).bot # weixin_subscription_bot 
debug_group = bot.get_chat(420074357)
channel = bot.get_chat('@web_record')
link_status = plain_db.load('existing')

@log_on_fail(debug_group)
@itchat.msg_register(SHARING, isGroupChat=True)
def group(msg):
	print('msg.Url', msg.Url)
	if not msg.Url or matchKey(msg.Url, BLACKLIST):
		return
	title = getTitle(msg.Url)
	if link_status.get(title, 0) >= 2:
		return # sent before
	if matchKey(msg.User.NickName, ['女权', '平权', 'hardcore', 'dykes']):
		link_status.inc(title, 2)
	else:
		link_status.inc(title, 1)
	if link_status.get(title) >= 2:
		channel.send_message(msg.Url)

def forwardToDebugChannel(msg):
	name = msg.User.get('RemarkName') or msg.User.NickName
	if 'mute' in name:
		return
	result = itchat.search_friends(userName=msg.FromUserName)
	if result and 'unzhi' in result.get('NickName'):
		recieve_type = 'to'
	else:
		recieve_type = 'from'
	cap = '%s %s' % (recieve_type, name)
	if msg.type in [TEXT, SHARING]:
		debug_group.send_message('%s: %s' % (cap, msg.Url or msg.text))
	else:
		msg.download(msg.fileName)
		if msg.type == PICTURE:
			debug_group.send_photo(open(msg.fileName, 'rb'), 
				caption=cap, timeout = 20 * 60)
		else:
			debug_group.send_document(open(msg.fileName, 'rb'), 
				caption=cap, timeout = 20 * 60)
		os.system('rm ' + msg.fileName)

@log_on_fail(debug_group)
@itchat.msg_register([TEXT, SHARING, PICTURE, RECORDING, 
	ATTACHMENT, VIDEO], isFriendChat=True)
def friend(msg):
	forwardToDebugChannel(msg)
	
itchat.auto_login(enableCmdQR=2, hotReload=True)
itchat.run(True)