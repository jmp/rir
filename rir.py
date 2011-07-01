#!/usr/bin/env python
#-*- coding: utf-8 -*-

import socket


class Rir:

    def __init__(self, nick='rir', host='irc.oftc.net', port=6667, users=[]):
        """Rir initializer"""
        self.nick = nick
        self.host = host
        self.port = port
        self.users = users
        self.done = False

    def connect(self):
        """Connect to the IRC server"""
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.host, self.port))
        self.irc.send('USER %s localhost %s :%s\r\n' % (self.nick, self.host, self.nick))
        self.irc.send('NICK %s\r\n' % self.nick)

    def quit(self):
        self.irc.send('QUIT :rir\r\n')
        self.irc.close()
        self.done = True

    def parse(self, line):
        """Parse incoming message"""
        print '<-', line.strip()
        info = line.split(':')
        # Reply to server ping
        if info[0].strip() == 'PING':
            self.irc.send('PONG :%s\r\n' % info[1])
            print '-> PONG :%s' % info[1]
        elif info[0]:
            return
        # Not a ping request, so parse the message
        msg = dict.fromkeys(['text', 'type', 'to', 'nick', 'host'], '')
        try:
            # Split line into message parts
            info, msg['text'] = line.split(':', 2)[1:]
            info, msg['type'], msg['to'] = info.split()
            msg['nick'], msg['host'] = info.split('!')
        except:
            pass
        # Bot is addressed by its nick
        if msg['text'].startswith(self.nick + ':'):
            cmd = msg['text'].split(self.nick + ':', 1)[1].strip()
            self.execute(cmd, msg)
        # Bot is addressed via PRIVMSG
        elif msg['type'] == 'PRIVMSG' and msg['to'] == self.nick:
            cmd = msg['text']
            self.execute(cmd, msg)

    def execute(self, cmd, msg):
        """Execute a command"""
        # Kill bot
        if cmd == 'die' or cmd.lower().startswith('quit'):
            if msg['host'] in self.users:
                self.quit()
        # Send a raw command
        elif len(cmd) > 2:
            if msg['host'] in self.users:
                self.irc.send('%s\r\n' % cmd)
                print '->', cmd

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

if __name__ == '__main__':
    bot = Rir()
    bot.connect()
    bot.loop()
