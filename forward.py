#!/usr/bin/env python
# -*- coding: utf-8 -*-

WC_GROUP_WHITELIST = ['女权讨论', '平权讨论', 'hardcore', 'dykes', '随记']

BLACKLIST = ['waerrpage', 'MzIwOTkzNzQ0MQ', 'Panziye4869', 'Artemis', 
	'support.weixin.qq.com', 'volition', 'MzI5NzUxMDU4OQ', '/promo/', 
	'MzI0ODg4NDM5Mw', 'MzAwNjgzMTQ5NQ', 'MzIyOTQyNDY2OQ', 'MzU2ODAyMTc3MQ',
	'MzU4NTc3NzA4Mg', 'MzU1MzgyMzg4Mg', 
	'MzIxNzA3NDQ5NQ', 'MzIzMDY2OTE2Nw', 'MzIwMzAwMzQxNw', 'MzU4NDU2MTA3MQ',
	'MzI3MDYxMjI0OQ', 'MzI5NjE5ODA1MA', 'MzI5MTQ0MDkzMw', 'MzAwMjY1ODE4OQ',
	'MzIwNzIzOTIzNQ', 'MzUzNDA0MjI5OA', 'MzI1MDUwMzcxNw', 'MzI5ODMzMDU3OA',
	'MzUyMTMzODAzMQ', 'MzI3ODE0Nzk4Mw', 'MzU3MDcwNDU0Nw', 'kg.qq.com',
	'MzAxMTg5Nzg4NQ', '小菜', 'cpu.baidu', 'MzUxOTEwMzc3Ng', '林米路', '学习强国',
	'MzAxNjI2MzM1MQ', '中国人', 'gongyi.qq', 'playsong.html'
]

LECTURE_KEYS = ['MzU0NTI2OTk5MA', 'MzI5OTIzNjE3OA', '讲座']

from telegram.ext import Updater
import itchat
from itchat.content import *
from telegram_util import matchKey, log_on_fail, clearUrl
from common import getFile
from export_to_telegraph import getTitle
import export_to_telegraph
import os
import plain_db

bot = Updater(getFile('credential')['bot_token'], use_context=True).bot # weixin_subscription_bot 
debug_group = bot.get_chat(420074357)
web_record = bot.get_chat('@web_record')
lecture_info = bot.get_chat('@lecture_info')
feminism_private_group = bot.get_chat(-1001239224743)
link_status = plain_db.load('existing', isIntValue=False)

def sendUrl(url, title, msg):
	if matchKey(title + url, LECTURE_KEYS):
		lecture_info.send_message(export_to_telegraph.export(
			url) or url)
		return True

	sender = msg.get('ActualNickName') or '1'
	if sender in BLACKLIST:
		return False
	
	wc_group = msg.User.get('NickName')
	if matchKey(wc_group, WC_GROUP_WHITELIST):
		web_record.send_message(url)
		return True

	# an article is shared by two different users
	if link_status.get(title) and link_status.get(title) != sender:
		web_record.send_message(url)
		return True
		
	link_status.update(title, sender)
	return False

@log_on_fail(debug_group)
def sendToWebRecord(msg):
	url = clearUrl(msg.Url)
	if not url or matchKey(url, BLACKLIST):
		return
	title = ''.join(getTitle(url).split())
	# 2,3 is legacy value
	if link_status.get(title) in ['2', '3', 'sent']: 
		return
	if sendUrl(url, title, msg):
		link_status.update(title, 'sent')

@log_on_fail(debug_group)
def forwardToChannel(msg, channel = debug_group):
	name = (msg.get('ActualNickName') or 
		msg.User.get('RemarkName') or msg.User.get('NickName') or '')
	if 'mute' in name:
		return
	result = itchat.search_friends(userName=msg.FromUserName)
	if result and 'unzhi' in result.get('NickName'):
		recieve_type = 'to'
	else:
		recieve_type = 'from'
	cap = '%s %s' % (recieve_type, name)
	if channel.id != debug_group.id:
		cap = name
	if msg.type in [TEXT, SHARING]:
		channel.send_message('%s: %s' % (cap, 
			clearUrl(msg.Url) or msg.text))
	else:
		os.system('mkdir tmp1 > /dev/null 2>&1')
		fn = 'tmp1/' + msg.fileName
		r = msg.download(fn)
		if msg.type == PICTURE:
			try:
				channel.send_photo(open(fn, 'rb'), 
					caption=cap, timeout = 20 * 60)
			except Exception as e:
				if not matchKey(str(e), ['File must be non-empty']):
					raise e
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
	if matchKey(msg.User.get('NickName'), ['一期一会']):
		forwardToChannel(msg, feminism_private_group)
	if msg.type == SHARING:
		sendToWebRecord(msg)
	
itchat.auto_login(enableCmdQR=2, hotReload=True)
itchat.run(True)