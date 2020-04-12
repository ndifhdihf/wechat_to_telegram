#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
import itchat
import time
from itchat.content import *
from telegram_util import matchKey, log_on_fail
from common import getFile
from contact import Contact
import os

tele = Updater(getFile('credential')['bot_token'], use_context=True)
bot = tele.bot
debug_group = bot.get_chat(-1001198682178)
channel = bot.get_chat('@web_record')
link_status = {}
contact = Contact()

@log_on_fail(debug_group)
@itchat.msg_register(SHARING, isGroupChat=True)
def group(msg):
	if not msg.Url:
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

@log_on_fail(debug_group)
@itchat.msg_register([TEXT, SHARING, PICTURE, RECORDING, 
	ATTACHMENT, VIDEO], isFriendChat=True)
def friend(msg):
	name = msg.user.get('RemarkName') or msg.User.NickName
	if 'mute' in name:
		return
	print(msg)
	if getFile('credential')['me'] in msg.FromUserName:
		recieve_type = 'to'
		contact.add(name, msg.ToUserName)
	else:
		recieve_type = 'from'
		contact.add(name, msg.FromUserName)
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
def bot_group(update, context):
	msg = update.message
	if not msg:
		return
	if msg.chat_id != debug_group.id or not msg.text:
		return
	r_msg = msg.reply_to_message
	if not r_msg or not r_msg.text:
		return
	name = r_msg.text.split(':')[0].split(' ')[-1]
	if name not in contact.contact:
		return
	itchat.send(msg.text, toUserName=contact.contact[name])

tele.dispatcher.add_handler(MessageHandler(Filters.group, bot_group), group = 3)

itchat.auto_login(enableCmdQR=2, hotReload=True)
itchat.run(True)