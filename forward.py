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

bot = Updater(token, use_context=True).bot # weixin_subscription_bot 
debug_group = bot.get_chat(420074357)
existing = plain_db.loadKeyOnlyDB('existing')
blocklist = plain_db.loadKeyOnlyDB('blocklist')
subscription = plain_db.loadKeyOnlyDB('subscription')

def getPrefix(msg):
	name = (msg.get('ActualNickName') or 
		msg.User.get('RemarkName') or msg.User.get('NickName') or '')
	result = itchat.search_friends(userName=msg.FromUserName)
	if result and 'unzhi' in result.get('NickName'):
		recieve_type = 'to'
	else:
		recieve_type = 'from'
	# TODO: get group name
	return '%s %s' % (recieve_type, name)

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
	if existing.get(msg_hash):
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
def groupToTelegram(msg):
	if matchKey(getRawContent(msg), blocklist.items()):
		return
	if matchKey(getRawHash(msg), subscription.items()):
		forward(msg)

@log_on_fail(debug_group)
@itchat.msg_register([SYSTEM], isGroupChat=True)
def system(msg):
	print('system message, looking for join', msg)
	
if __name__ == '__main__':
	itchat.auto_login(enableCmdQR=2, hotReload=True)
	itchat.run(True)