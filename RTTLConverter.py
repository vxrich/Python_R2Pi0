import time
import thread 
import re

def controllo(stringa, default):
	if stringa == None:
		return default
	else:
		return int(stringa)

def loadData (nomefile):
	
	with open(nomefile, 'r') as note:
		strnote = note.readline()
	
	#Leva a capo e punti
	strnote = strnote.strip('\n.')	
	
	#Separa nelle 3 parti di cui sono composti i file RTTTL:
	#0. nome -> non usato
	#1. [ottava_base, bpm, durata_nota] -> valori
	#2. note
	tutto = strnote.split(':')
	valori = tutto[1].split(',')
	note = tutto[2].split(',')
	valoriInit = []
	
	#Trasforma in int, leva le lettere e l'uguale
	for i in valori:
		valoriInit.append(int(re.search('[0-9]+', i).group(0)))
	
	listaNote = []
	
	for i in note:
		i = i.upper()
		
		#Separa le 3 info che ci sono per ogni nota: (durata)(nota)(ottava)
		match = re.search('([0-9]+)?([A-Z#]+)([0-9]+)?', i)
		tupla = (controllo(match.group(1), valoriInit[0]), match.group(2), controllo(match.group(3), valoriInit[1]))
		listaNote.append(tupla)
		
		
	return (valoriInit, listaNote)	

def durataControl(durata):
	durate = [1,2,4,8,16,32]
	if durata in durate:
		return durata
	else:
		return 1
		
def noteToFrequency(nota, ottava):
	note = {'A':27.50,'A#':29.14,'B':30.87,'C':16.35,'C#':17.32,'D':18.35,'D#':19.45,'E':20.60,'F':21.83,'F#':23.12,'G':24.50,'G#':25.96,'P':0.0001}
	frequenza = note[nota]
	multiplier = 2**ottava
	return frequenza*multiplier
	
def durataCalc(durata, bpm):
	colpo = float((60.0/bpm)*4)
	return float(colpo/durata)

#Deprecata
def durataCalcComp(durata, bpm):
	colpo = float(60.0/bpm)
	return colpo-float(colpo/durata)
	
def getter(fileName):
	valori = loadData(fileName)
	bpm = valori[0][2]
	triplette = valori[1]
	note = []

	for i in range(len(triplette)):
		note.append((noteToFrequency(triplette[i][1], triplette[i][2]), durataCalc(triplette[i][0], bpm), durataCalcComp(triplette[i][0], bpm)))
	return note
	



