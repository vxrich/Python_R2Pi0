from distutils.core import setup, Extension

module1 = Extension('proxsensor',
                    include_dirs = ['/usr/local/include' ,'/usr/local/lib'],
                    libraries = ['wiringPi'],
                    library_dirs = ['/usr/local/lib'],
                    sources = ['proxSensor.c', 'pythonizedProxSensor.c'])

setup (name = 'proxsensor',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
