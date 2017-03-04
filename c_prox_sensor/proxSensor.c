/*
*   Autori: Tosatto Davide, Grespan Riccardo
*
*   Modulo di controllo del sensore ad ultrasuoni per la rilevazione della distanza.
*
*   Si è deciso di scrivere questo modulo in C perche, per leggere la distanza
*   e necessario misurare la durata di un'impulso, cosa che, fatta attraverso polling,
*   va ad utilizzare troppe risorse di calcolo, in quanto non si possono inserire
*   sleep nel ciclo per mantenere una precisione accettabile.
*
*   Abbiamo pertanto utilizzato wiringPi, che, nella sua versione C, permette di
*   mettersi in ascolto di variazioni sui pin di I/O attraverso il meccanismo degli
*   interrupt e quindi senza spreco di risorse di calcolo
*
*   In questo file abbiamo il modulo in C puro. Nel file pythonizedProxSensor.c
*/

#include "proxSensor.h"
#include <time.h>
#include <wiringPi.h>
#include <stdio.h>

static int ECHO_PIN = 0;
static int TRIG_PIN = 0;
static int done = 1;
static float dist = 0;
unsigned long int t1,t2;
const int SOUND_CONST = 171.50;

static float getMillisDiff (clock_t t1, clock_t t2);
static float getDistFromTime (float timeDiff);

static void edge ();

void initProxSensor (int echoPin, int trigPin)
{
    ECHO_PIN = echoPin;
    TRIG_PIN = trigPin;
    pinMode(ECHO_PIN, INPUT);
    pinMode(TRIG_PIN, OUTPUT);
    pullUpDnControl(TRIG_PIN, PUD_DOWN);
    wiringPiISR (ECHO_PIN, INT_EDGE_BOTH,  edge);
}

void startReading ()
{
    done = 0;

    digitalWrite(TRIG_PIN,HIGH);
    delay(1);
    digitalWrite(TRIG_PIN,LOW);
}

int readingDone ()
{
    return done;
}

float getDist()
{
    return dist;
}

//Calcola la differenza e passa da micrsecondi a millisecondi
static float getMillisDiff (clock_t t1, clock_t t2)
{
    return ((float)(t1 - t2) / 1000);
}

//Calcola la distanza dalla differenza in millisecondi
static float getDistFromTime (float timeDiff)
{
    return (timeDiff/1000.0)*SOUND_CONST;
}

//Funzione callback richiamata al rilevamento di un fronte sul piedino ECHO_PIN
static void edge ()
{
    if (done)
        return;

    if (digitalRead(ECHO_PIN) == HIGH)
    {
        t1 = micros();
    }
    else
    {
        t2 = micros();

        dist = getDistFromTime(getMillisDiff(t2, t1));
        done = 1;

    }
}
