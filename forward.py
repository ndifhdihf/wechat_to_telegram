#!/usr/bin/env python
# -*- coding: utf-8 -*-

BLACKLIST = ['waerrpage', 'MzIwOTkzNzQ0MQ', 'Panziye4869', 'Artemis', 
	'support.weixin.qq.com', 'volition']

from telegram.ext import Updater
import itchat
from itchat.content import *
from telegram_util import matchKey, log_on_fail
from common import getFile
import os

bot = Updater(getFile('credential')['bot_token'], use_context=True).bot
debug_group = bot.get_chat(-1001198682178)
channel = bot.get_chat('@web_record')
link_status = {}

@log_on_fail(debug_group)
@itchat.msg_register(SHARING, isGroupChat=True)
def group(msg):
	if not msg.Url or matchKey(msg.Url, BLACKLIST):
		return
	link_status[msg.FileName] = link_status.get(msg.FileName, 0)
	if link_status[msg.FileName] >= 1:
		return # sent before
	if matchKey(msg.User.NickName, ['女权', '平权', 'hardcore', 'dykes']):
		link_status[msg.FileName] += 1
	else:
		link_status[msg.FileName] += 0.5
	if link_status[msg.FileName] >= 1:
		channel.send_message(msg.Url)

def forwardToDebugChannel(msg):
	name = msg.User.get('RemarkName') or msg.User.NickName
	if 'mute' in name:
		return
	if 'yunzhi' in msg.User.NickName:
		recieve_type = 'to'
	else:
		recieve_type = 'from'
	cap = '%s %s' % (recieve_type, name)
	if msg.type == TEXT:
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

@log_on_fail(debug_group)
@itchat.msg_register([TEXT, SHARING, PICTURE, RECORDING, 
	ATTACHMENT, VIDEO], isGroupChat=True)
def pythonGroup(msg):
	if 'python' in str(msg.User.NickName).lower():
		forwardToDebugChannel(msg)
	
itchat.auto_login(enableCmdQR=2, hotReload=True)
itchat.run(True)