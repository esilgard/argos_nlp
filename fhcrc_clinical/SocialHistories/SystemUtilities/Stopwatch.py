"""Stopwatch function and time formats taken from this stack overflow answer:
 http://stackoverflow.com/questions/5890304/stopwatch-in-python"""


def stopWatch(value):
    '''From seconds to Days;Hours:Minutes;Seconds'''

    valueD = (((value/365)/24)/60)
    Days = int (valueD)

    valueH = (valueD-Days)*365
    Hours = int(valueH)

    valueM = (valueH - Hours)*24
    Minutes = int(valueM)

    valueS = (valueM - Minutes)*60
    Seconds = int(valueS)

    return Days,";",Hours,":",Minutes,";",Seconds
