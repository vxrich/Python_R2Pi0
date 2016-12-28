# -*- coding: utf-8 -*-

import blue
import bluetooth
import threading
import select
import time



TIMEOUT = 0.5

class Server:
	_subservers = []
	_commands = {}
	_cycle_thread = None
	_stop = False
	
	def __init__ (self, commands):
		self._commands = commands
		t = threading.Thread(target=self._cycle)
		self._cycle_thread = t
		
	def start(self):
		self._cycle_thread.start()
		
	def _cycle (self):
		while not self._stop:
			conn = blue.acceptConnection(0.5)
			
			if conn != None:
				subs = Subserver(conn, self._commands)
				subs.start()
				self._subservers.append(subs)
			
	def stop (self):
		self._stop = True
		self._cycle_thread.join()
		
		for subs in self._subservers:
			subs.stop()
		

class Subserver:
	_stop = False
	_thread = None
	_addr = None
	_connection = None
	_commands = {}
	
	def  __init__ (self, connection, commands, blocking=False):
	
		connection[0].setblocking(0)
		connection[0].settimeout(0.5)
	
		self._connection, self._addr = connection
		self._commands = commands		
		
		print "Subserver created"
		
	def start(self, blocking=False):
	
		if not blocking:
			t = threading.Thread(target=self._cycle)
			self._thread = t
			t.start()
		else:
			self._cycle()
			
		print "Subserver started"
		
	def _executeCommand (self, data):
		cmd = data.split( )
		
		if len(cmd) > 0:
			print "Command received %s" % data
			print "Command received %s" % str(cmd)
			if cmd[0] in self._commands:
				self._commands[cmd[0]](cmd, self)
		else:
			self.send("ko")
		
	def _cycle (self):
		while not self._stop:
		
			try:
				read = ""
				data = ""
				while (not read.startswith(";")):
					#Ricevo un byte alla volta, comandi terminati da ";"
					read = self._connection.recv(1)
					# print "Read %s" % read
					data+=read
					print "Read %s" % read
				self._executeCommand(data[0:len(data)-1])
				
			except bluetooth.BluetoothError as e:
				msg = str(e)
				
				if "unavailable" in msg:
					self._stop = True
					
	def send (self, msg):
		try:
				#self._connection.send(msg)
				pass
		except bluetooth.BluetoothError:
			pass
		
			
	def stop (self):
		self._stop = True
		self._thread.join()
		self._connection.close()
		

if __name__=="__main__":
	
	import r2pi0_V2