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
	users = itchat.search_friends(name=name)
	if not users:
		debug_group.send('No user name: %s' % name)
		return
	itchat.send(text, toUserName=users[0]['UserName'])

@log_on_fail(debug_group)
def bot_group(update, context):
	msg = update.message
	if not msg:
		return
	if msg.chat_id != debug_group.id or not msg.text:
		return
	r_msg = msg.reply_to_message
	if not r_msg:
		return
	cap = r_msg.text or r_msg.caption
	if not cap:
		return
	name = cap.split(':')[0].split(' ')[-1]
	try:
		sendMsg(name, msg.text)
	except:
		itchat.auto_login(enableCmdQR=2, hotReload=True)
		sendMsg(name, msg.text)

tele.dispatcher.add_handler(MessageHandler(Filters.group, bot_group), group = 3)
tele.start_polling()
tele.idle()