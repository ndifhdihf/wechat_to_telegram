#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
import itchat
from telegram_util import log_on_fail, isUrl, splitCommand, commitRepo
import cached_url
from common import getFile
import time
import os
from export_to_telegraph import getTitle
import plain_db

blocklist = plain_db.loadKeyOnlyDB('blocklist')

tele = Updater(getFile('credential')['bot_token'], use_context=True)
bot = tele.bot
debug_group = bot.get_chat(420074357)
feminism_private_group = bot.get_chat(-1001239224743)
wechat_feminism_group_name = '一期一会'

last_login_time = 0

def sendMsg(name, text):
	users = (itchat.search_friends(name)
		or itchat.search_friends(remarkName = name)
		or itchat.search_friends(nickName = name))
	if not users:
		debug_group.send_message('No user name: %s' % name)
		return
	itchat.send(text, toUserName=users[0]['UserName'])
	debug_group.send_message('success')

def login():
	global last_login_time
	if time.time() - last_login_time > 60 * 60:
		itchat.auto_login(enableCmdQR=2, hotReload=True)
		last_login_time = time.time()

def getPrefix(telegram_msg):
	if telegram_msg.from_user.first_name != 'Yunz':
		return 'From ' + msg.from_user.first_name + ': '
	return ''

def decorate(text):
	if isUrl(text) and len(text.split()) == 1:
		return getTitle(text) + ' ' + text 
	return text

def sendToFeminismPrivateGroup(msg):
	search_result = itchat.search_chatrooms(
		name = wechat_feminism_group_name)
	if not search_result:
		return
	chatroom_id = search_result[0]['UserName']
	os.system('mkdir tmp2 > /dev/null 2>&1')
	if msg.text:
		text = getPrefix(msg) + decorate(msg.text)
		itchat.send(text, chatroom_id)
		msg.chat.send_message(text)
	elif msg.photo:
		file = msg.photo[0].get_file()
		fn = file.download(cached_url.getFilePath(file.file_path))
		itchat.send_image(fn, toUserName=chatroom_id)
		msg.forward(feminism_private_group.id)
	elif msg.document:
		file = msg.document.get_file()
		fn = file.download('tmp2/' + msg.document.file_name)
		itchat.send_file(fn, toUserName=chatroom_id) 
		msg.forward(feminism_private_group.id)
	else:
		return
	msg.delete()

@log_on_fail(debug_group)
def replyGroup(update, context):
	msg = update.message
	if not msg:
		return
	if msg.chat_id == feminism_private_group.id:
		login()
		sendToFeminismPrivateGroup(msg)

@log_on_fail(debug_group)
def reply(update, context):
	msg = update.message
	if not msg or not msg.text:
		return
	if msg.chat.username not in [debug_group.username, 'web_record']:
		return
	command, text = splitCommand(msg.text)
	if command == '/abl':
		blocklist.add(text)
		msg.reply_text('success')
		commitRepo(delay_minute=0)
		return

	if msg.chat_id != debug_group.id:
		return
	r_msg = msg.reply_to_message
	if not r_msg:
		return
	cap = r_msg.text or r_msg.caption
	if not cap:
		return
	name = cap.split(':')[0].lstrip('from').lstrip('to').strip()
	login()
	sendMsg(name, msg.text)

if __name__ == '__main__':
	tele.dispatcher.add_handler(MessageHandler(Filters.private, reply), group = 3)
	tele.dispatcher.add_handler(MessageHandler(Filters.group, replyGroup), group = 4)
	tele.start_polling()
	tele.idle()