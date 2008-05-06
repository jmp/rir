#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Copyright 2008 Jarkko Piiroinen <jarkkop@iki.fi>.
Distributed under the terms of GNU General Public License, version 3. 
"""

import socket

class Rir:
	def __init__(self, nick='rir', host='irc.oftc.net', port=6667, users=['ident@hostname']):
		"""Rir initializer"""
		self.nick = nick
		self.host = host
		self.port = port
		self.users = users
		self.done = False

	def connect(self):
		"""Connect to IRC"""
		self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.irc.connect((self.host, self.port))
		self.irc.send('USER %s localhost %s :%s\r\nNICK %s\r\n' % (self.nick, self.host, self.nick, self.nick))

	def parse(self, line):
		"""Parse incoming message"""
		print '<-', line
		info = line.split(':')
		# Reply to server ping
		if info[0].strip() == 'PING':
			self.irc.send('PONG :%s\r\n' % info[1])
			print '-> PONG :%s' % info[1]
		# Not a ping request, so parse the message
		elif not info[0]:
			msg = {'text':'', 'from':'', 'type':'', 'to':'', 'nick':'', 'host':''}
			try:
				# Split line into message parts
				info, msg['text'] = line.split(':', 2)[1:]
				info, msg['type'], msg['to'] = info.split()
				msg['nick'], msg['host'] = info.split('!')
			except:
				pass
				
			# Check if the bot is addressed by its nick or via PRIVMSG
			if msg['host'] in self.users and (msg['text'].startswith(self.nick + ':') or
			  (msg['type'] == 'PRIVMSG' and msg['to'] == self.nick)):
			  	if msg['type'] == 'PRIVMSG' and msg['to'] == self.nick:
			  		command = msg['text']
			  	else:
					command = msg['text'].split(self.nick + ':', 1)[1].strip()
				# Kill bot
				if command == 'die' or command.lower().startswith('quit'):
					self.irc.send('QUIT :rir\r\n')
					self.irc.close()
					self.done = True
				# Avoid sending useless commands to server
				elif len(command) > 2:
					# Send raw command
					self.irc.send('%s\r\n' % command)
					print '->', command

	def loop(self):
		"""Receive data from server for as long as possible"""
		buffer = ''
		while not self.done:
			# Receive data from server
			buffer += self.irc.recv(4096)
			buffer = buffer.split('\r\n')
			# Parse each line received
			for line in buffer[:-1]:
				self.parse(line)
			buffer = buffer[-1]

def main():
	"""The main function"""
	bot = Rir()
	bot.connect()
	bot.loop()

if __name__ == '__main__': main()
