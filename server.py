# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo di comunicazione attraverso bluetooth con app Android residente sul telefono
#
import blue
import bluetooth
import threading
import select
import time



TIMEOUT = 0.5

EVENT_CLIENT_CONNECTED = 0
EVENT_CLIENT_DISCONNECTED = 1

class Server:
	"""
		Classe server. Si occupa di ricevere le richieste di connessione dall'esterno
		e di avviare un'istanza di Subserver in un thread separato per ogni richiesta.
	"""
	def __init__ (self, commands):

		self._listeners = []
		self._subservers = []
		self._stop = False
		self._commands = commands
		t = threading.Thread(target=self._cycle)
		self._cycle_thread = t

	def addListener (self, lst):
		self._listeners.append(lst)

	def removeListener (self, lst):
		self._listeners.remove(lst)

	def _fireEvent (self, evt, param):
		for lst in self._listeners:
			print "Main fired, " + str(self._listeners)
			lst(evt, param)

	def _receiveSubEvent (self, evt, subs):
		self._fireEvent(evt,subs)

	def start(self):
		self._cycle_thread.start()

	def _cycle (self):
		while not self._stop:
			conn = blue.acceptConnection(0.5)

			if conn != None:
				subs = Subserver(conn, self._commands)
				subs.addListener(self._receiveSubEvent)
				subs.start()

				self._subservers.append(subs)


	def stop (self):
		self._stop = True
		self._cycle_thread.join()

		for subs in self._subservers:
			subs.stop()


class Subserver:
	"""
		Risponde ai comandi impartiti da un singolo client.
		Riceve una lista di comandi con rispettivi callback nel costruttore
		in modo da risultare il più generale possibile
	"""

	def  __init__ (self, connection, commands, blocking=False):

		self._stop = False
		self._thread = None
		self._addr = None
		self._connection = None

		connection[0].setblocking(0)
		connection[0].settimeout(0.5)

		self._connection, self._addr = connection
		self._commands = commands

		self._listeners = []

		print "Subserver created"

	def addListener (self, lst):
		self._listeners.append(lst)

	def removeListener (self, lst):
		self._listeners.remove(lst)

	def _fireEvent (self, evt, param):
		for lst in self._listeners:
			print "Sub fired, " + str(self._listeners)
			lst(evt, param)

	def start(self, blocking=False):

		if not blocking:
			t = threading.Thread(target=self._cycle)
			self._thread = t
			t.start()
		else:
			self._cycle()

		self._fireEvent(EVENT_CLIENT_CONNECTED, self)

		print "Subserver started"

	def _executeCommand (self, data):
		cmd = data.split( )

		if len(cmd) > 0:
			print "Command received %s" % data
			print "Command received %s" % str(cmd)

			#Controlla se il comando è nella lista dei comandi passati.
			#Se si, esegue il corrispondente callback
			if cmd[0] in self._commands:
				self._commands[cmd[0]](cmd, self)
		else:
			self.send("ko")

	def _cycle (self):
		while not self._stop:

			try:
				read = ""
				data = ""
				while (not read.endswith(";")):
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
		self._fireEvent(EVENT_CLIENT_DISCONNECTED, self)


if __name__=="__main__":

	import r2pi0_V2
