#include <Python.h>
#include <wiringPi.h>
#include "proxSensor.h"

static PyObject * proxsensor_getDistance (PyObject *self, PyObject *args);
static PyObject * proxsensor_initialize (PyObject *self, PyObject *args);
static PyObject * proxsensor_startReading (PyObject *self, PyObject *args);
static PyObject * proxsensor_readingDone (PyObject *self, PyObject *args);

static PyMethodDef module_methods[] = {
    {"getDistance", proxsensor_getDistance, METH_VARARGS, "Ritorna la distanza"},
    {"initialize", proxsensor_initialize, METH_VARARGS, "Inizializza il modulo"},
    {"startReading", proxsensor_startReading, METH_VARARGS, "Inizia la lettura"},
    {"readingDone", proxsensor_readingDone, METH_VARARGS, "Dice se la lettura è finita o no"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initproxsensor(void)
{
    PyObject *m = Py_InitModule3("proxsensor", module_methods, "Modulo che controlla il sensore di prossimità con interrupts");
    if (m == NULL)
        return;
}


//----------FUNZIONI ESPORTATE-------------------

static PyObject * proxsensor_getDistance (PyObject *self, PyObject *args)
{
    return PyFloat_FromDouble(getDist());
}

static PyObject * proxsensor_initialize (PyObject *self, PyObject *args)
{
    int echoPin, trigPin;
    
    //Serve per leggere due inter (ii) dagli argomenti passati
    if (!PyArg_ParseTuple(args, "ii", &echoPin, &trigPin))
        return PyInt_FromLong(1);

    wiringPiSetupGpio();
    
    initProxSensor(echoPin,trigPin);
    
    return PyInt_FromLong(0);
}

static PyObject * proxsensor_startReading (PyObject *self, PyObject *args)
{
    startReading();
    
    return PyInt_FromLong(0);
}

static PyObject * proxsensor_readingDone (PyObject *self, PyObject *args)
{
    return PyBool_FromLong(readingDone());
}