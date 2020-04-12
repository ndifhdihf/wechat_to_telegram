#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
import itchat
from telegram_util import log_on_fail
from common import getFile
from contact import Contact

tele = Updater(getFile('credential')['bot_token'], use_context=True)
bot = tele.bot
debug_group = bot.get_chat(-1001198682178)

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
	if not r_msg:
		return
	print(4)	
	cap = r_msg.text or r_msg.caption
	print(cap)
	if not cap:
		return
	name = cap.split(':')[0].split(' ')[-1]
	print(name)
	contact = Contact()
	if name not in contact.contact:
		return
	print(msg.text)
	itchat.send(msg.text, toUserName=contact.contact[name])

tele.dispatcher.add_handler(MessageHandler(Filters.group, bot_group), group = 3)
tele.start_polling()
tele.idle()