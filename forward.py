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
web_record = bot.get_chat('@web_record')
feminism_private_group = bot.get_chat(-428192067)
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
		web_record.send_message(msg.Url)

def forwardToChannel(msg, channel = debug_group):
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
		channel.send_message('%s: %s' % (cap, msg.Url or msg.text))
	else:
		os.system('mkdir tmp > /dev/null 2>&1')
		fn = 'tmp/' + msg.fileName
		msg.download(fn)
		print('testing 1', msg.type)
		if msg.type == PICTURE:
			channel.send_photo(open(fn, 'rb'), 
				caption=cap, timeout = 20 * 60)
		else:
			channel.send_document(open(fn, 'rb'), 
				caption=cap, timeout = 20 * 60)
		os.system('rm ' + fn)

@log_on_fail(debug_group)
@itchat.msg_register([TEXT, SHARING, PICTURE, RECORDING, 
	ATTACHMENT, VIDEO], isFriendChat=True)
def friend(msg):
	forwardToChannel(msg)

@log_on_fail(debug_group)
@itchat.msg_register([TEXT, SHARING, PICTURE, RECORDING, 
	ATTACHMENT, VIDEO], isGroupChat=True)
def groupToTelegram(msg):
	if not matchKey(msg.User.get('NickName'), ['随记']):
		return
	forwardToChannel(msg, feminism_private_group)
	
itchat.auto_login(enableCmdQR=2, hotReload=True)
itchat.run(True)