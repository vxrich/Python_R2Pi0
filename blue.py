#########################################################
#														#
#		Author: Riccardo Grespan						#
#				Davide Tosatto							#
#														#
#  		Bluetooth communication utility functions.   	#
#		For testing install BluetoothViewer on 			#
#		an android device and try to connect and		#
#		send messages (after running this script)		#
#														#
#########################################################
import bluetooth

def search():
	"""
		Cerca i device bluetooth vicini e
		ritorna una lista di tuple (indirizzo-mac, nome)
	"""
	return bluetooth.discover_devices(lookup_names=True)

def connect(addr):
	"""
		Si collega ad un device bluetooth. Ritorna il socket.
		Puo' causare un'eccezione
	"""
	sock = bluetooth.BluetoothSocket (bluetooth.L2CAP)
	sock.connect((addr, 0x1001))
	
def acceptConnection():
	"""
		Si mette in ascolto per una nuova connessione.
		E' bloccante. Ritrona una tupla (socket, indirizzo)
	"""
	server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
		
	port = 1
	server_sock.bind(("",port))
	server_sock.listen(1)
	
	print "Listening"

	res = server_sock.accept()
	server_sock.close()
	return res

#Main, per test
if (__name__=="__main__"):
#	nearby_devices=search()
#	print("found %d devices" % len(nearby_devices))

#	for addr, name in nearby_devices:
#		print("  %s - %s" % (addr, name))

	client_sock,address = acceptConnection()
	print "Accepted connection from ",address
	
	data = ""
	
	while data!="exit":
		data = client_sock.recv(1024)
		data = data.strip('\n')	
		print "received [%s]" % data
		client_sock.send("ok")