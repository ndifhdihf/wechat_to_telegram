#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
import itchat
from telegram_util import log_on_fail
from common import getFile

tele = Updater(getFile('credential')['bot_token'], use_context=True)
bot = tele.bot
debug_group = bot.get_chat(-1001198682178)

def sendMsg(name, text):
	print(name, text)
	users = itchat.search_friends(name=name)
	if not users:
		debug_group.send_message('No user name: %s' % name)
		return
	print(users[0]['UserName'])
	itchat.send(text, toUserName=users[0]['UserName'])

@log_on_fail(debug_group)
def bot_group(update, context):
	print(1)
	msg = update.message
	if not msg:
		return
	print(2)
	if msg.chat_id != debug_group.id or not msg.text:
		return
	print(3)
	r_msg = msg.reply_to_message
	print(4)
	if not r_msg:
		return
	print(5)
	cap = r_msg.text or r_msg.caption
	if not cap:
		return
	print(6)
	name = cap.split(':')[0].split(' ')[-1]
	print(7, name)
	try:
		sendMsg(name, msg.text)
	except:
		itchat.auto_login(enableCmdQR=2, hotReload=True)
		sendMsg(name, msg.text)

tele.dispatcher.add_handler(MessageHandler(Filters.group, bot_group), group = 3)
tele.start_polling()
tele.idle()