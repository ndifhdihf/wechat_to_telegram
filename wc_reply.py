#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
import itchat
from telegram_util import log_on_fail, isUrl
import cached_url
from common import token
import time
import os
from export_to_telegraph import getTitle

tele = Updater(token, use_context=True)
bot = tele.bot
debug_group = bot.get_chat(420074357)

last_login_time = 0

def decorate(text):
	if isUrl(text) and len(text.split()) == 1:
		return '【%s】 %s' % (getTitle(text), text)
	return text

def sendMsg(username, msg):
	os.system('mkdir tmp > /dev/null 2>&1')
	if msg.text:
		itchat.send(decorate(msg.text), toUserName=username)
	elif msg.photo:
		file = msg.photo[0].get_file()
		fn = file.download(cached_url.getFilePath(file.file_path))
		itchat.send_image(fn, toUserName=username)
	elif msg.document:
		file = msg.document.get_file()
		fn = file.download('tmp/' + msg.document.file_name)
		itchat.send_file(fn, toUserName=username) 
	else:
		msg.reply_text('fail to send')
		return
	msg.forward(debug_group.id)
	msg.delete()

def login():
	global last_login_time
	if time.time() - last_login_time > 60 * 60:
		itchat.auto_login(enableCmdQR=2, hotReload=True)
		last_login_time = time.time()

def getChat(cap):
	if ' in ' not in cap:
		name = cap.split(':')[0].lstrip('to').strip()
		users = (itchat.search_friends(name)
			or itchat.search_friends(remarkName = name)
			or itchat.search_friends(nickName = name))
		if not users:
			debug_group.send_message('No user name: %s' % name)
			return
		return users[0]['UserName']
	chat = cap.split(':')[0].split(' in ')[-1].strip()
	chats = (itchat.search_chatrooms(chat)
		or itchat.search_chatrooms(remarkName=chat)
		or itchat.search_chatrooms(nickName=chat))
	if not chats:
		debug_group.send_message('No chat name: %s' % chat)
		return
	return chats[0]['UserName']

@log_on_fail(debug_group)
def reply(update, context):
	msg = update.effective_message
	if not msg or not msg.text:
		return
	if msg.chat_id != debug_group.id:
		return
	r_msg = msg.reply_to_message
	if not r_msg:
		return
	cap = r_msg.text or r_msg.caption
	if not cap:
		return
	login()
	username = getChat(cap)
	if username:
		sendMsg(username, msg)

if __name__ == '__main__':
	tele.dispatcher.add_handler(MessageHandler(Filters.private, reply), group = 5)
	tele.start_polling()
	tele.idle()