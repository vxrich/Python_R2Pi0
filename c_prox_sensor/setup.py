# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Script per compilare ed installare il modulo proxsensor, scritto in C
#   Comando da eseguire: sudo python setup.py install
#

from distutils.core import setup, Extension

module1 = Extension('proxsensor',
                    include_dirs = ['/usr/local/include' ,'/usr/local/lib'],
                    libraries = ['wiringPi'],
                    library_dirs = ['/usr/local/lib'],
                    sources = ['proxSensor.c', 'pythonizedProxSensor.c'])

setup (name = 'proxsensor',
       version = '1.0',
       description = 'Pacchetto di sontrollo del sensore di prossimità',
       ext_modules = [module1])
