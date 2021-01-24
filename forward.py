#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater
import itchat
from itchat.content import *
from telegram_util import matchKey, log_on_fail, clearUrl
from common import token
from export_to_telegraph import getTitle
import os
import plain_db
import threading

bot = Updater(token, use_context=True).bot # weixin_subscription_bot 
debug_group = bot.get_chat(420074357)
existing = plain_db.loadKeyOnlyDB('existing')
blocklist = plain_db.loadKeyOnlyDB('blocklist')
subscription = plain_db.loadKeyOnlyDB('subscription')

def getPrefix(msg):
	name = (msg.get('ActualNickName') or 
		msg.User.get('RemarkName') or msg.User.get('NickName') or '')
	
	search_result = itchat.search_friends(userName=msg.FromUserName)
	if search_result and 'unzhi' in search_result.get('NickName'):
		recieve_type = 'to'
		chat_name = msg.ToUserName
	else:
		recieve_type = 'from'
		chat_name = msg.FromUserName

	search_result = itchat.search_chatrooms(userName=chat_name)
	if not search_result: # private chat
		return '%s %s' % (recieve_type, name)	

	chat = search_result.get('RemarkName') or search_result.get('NickName')
	if recieve_type == 'to':
		return 'to ' + chat
	return 'from %s in %s' % (name, chat)

def getRawHash(msg):
	if msg.type == TEXT:
		return msg.text
	if msg.type == SHARING:
		return getTitle(msg.Url)
	return msg.fileName

def getHash(msg):
	return ''.join(getRawHash(msg).split())[:10]

@log_on_fail(debug_group)
def sendFile(msg, prefix):
	os.system('mkdir tmp > /dev/null 2>&1')
	fn = 'tmp/' + msg.fileName
	r = msg.download(fn)
	if msg.type != PICTURE:
		debug_group.send_document(open(fn, 'rb'), caption=prefix, timeout = 20 * 60)
		return 
	try:
		debug_group.send_photo(open(fn, 'rb'), caption=prefix, timeout = 20 * 60)
	except Exception as e:
		if not matchKey(str(e), ['File must be non-empty']):
			raise e

@log_on_fail(debug_group)
def forward(msg):
	prefix = getPrefix(msg)
	if 'mute' in prefix:
		return
	msg_hash = getHash(msg)
	if existing.contain(msg_hash):
		return

	if msg.type in [TEXT, SHARING]:
		debug_group.send_message('%s: %s' % (prefix, clearUrl(msg.Url) or msg.text))
	else:
		sendFile(msg, prefix)
		os.system('rm ' + fn)

	existing.add(msg_hash)

@log_on_fail(debug_group)
@itchat.msg_register([TEXT, SHARING, PICTURE, RECORDING, 
	ATTACHMENT, VIDEO], isFriendChat=True)
def friend(msg):
	forward(msg)

def getRawContent(msg):
	content = [getPrefix(msg), msg.url, getRawHash(msg)]
	return '\n'.join([str(item) for item in content])

@log_on_fail(debug_group)
@itchat.msg_register([TEXT, SHARING], isGroupChat=True)
def group(msg):
	if matchKey(getRawContent(msg), blocklist.items()):
		return
	if matchKey(getRawHash(msg), subscription.items()):
		forward(msg)

@log_on_fail(debug_group)
def loopImp():
	search_result = itchat.search_chatrooms('【心理互助】你说我听')
	chat = search_result[0]
	for user in search_result[0].MemberList:
		if matchKey(user.get('NickName'), ['段誉', '风雨']):
			print('kick user', chat.get('NickName'), user.get('NickName')) 
			itchat.delete_member_from_chatroom(chat.UserName, uset.UserName)

def loop():
	loopImp()
	threading.Timer(60, loop).start()
	
if __name__ == '__main__':
	itchat.auto_login(enableCmdQR=2, hotReload=True)
	threading.Timer(1, loop).start()
	itchat.run(True)