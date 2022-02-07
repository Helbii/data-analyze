from ctypes import Union
from typing import Any

from pandas import Series

from lib import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Nebuleco:

    def __init__(self, name, connect):
        """
        :param string name : name of the nebuleco
        :param object connect: API connection
        """
        self.connect = connect
        self.name = name
        self.id = connect.getId(name)
        self.step = 0
        self.date = datetime.now()
        self.error = False
        self.lastLog = int(datetime.timestamp(datetime(self.date.year,self.date.month,self.date.day)) - 946684800)  #- relativedelta(days=5)'
        self.geographiczone = connect.getGeographicZone(self.id)
        self.voltage = connect.getValue('TENSIONPIEZO', self.lastLog, self.id, 10)
        self.pwm = connect.getValue('PWMNEBU', self.lastLog, self.id, 10)
        self.current = connect.getValue('CURRENTPIEZO', self.lastLog, self.id, 1)
        self.temperature = connect.getValue('TEMPERATURE', self.lastLog, self.id, 1)
        self.cptceramique = connect.getValue('COMPTEUR_CERAMQIUE', self.lastLog, self.id, 1)
        self.breakdown = self._indicator()

    def getLastlog(self):
        return datetime.fromtimestamp(self.lastLog)

    def getError(self) -> bool:

        return self.error

    def getBreakdown(self) -> list:

        return self.breakdown

    def getName(self) -> str:

        return self.name

    def getGeographicZone(self) -> str:

        return self.geographiczone

    def getcptCeramique(self) -> tuple[str, str]:
        '''

          :return: values, times
        '''
        values = self.cptceramique[1]
        times = self.cptceramique[0]

        return values, times

    def getrawCurrent(self) -> tuple[str, str]:
        '''

        :return: values, times
        '''
        return self.current

    def getPWM(self):
        time, value = self.pwm
        ntime=[]
        nvalue=[]
        try:
            for i in range(0, len(time)):
                time[i] = int(time[i])
                value[i] = float(value[i])

        except TypeError:
            value = 0
            time=self.lastLog
            return value, time
        if self.lastLog-time[len(time)-1] > 2592000:
            nvalue[0] = value[len(time)-1]
            nvalue[1] = nvalue[0]
            ntime[0] = self.lastLog - 2592000
            ntime[1] = self.lastLog
        else:
            return value, getDate(getGoodTimestamp(time))

        time=getDate(getGoodTimestamp(ntime))

        return nvalue, ntime

    def getrawTemperature(self) -> tuple[str, str]:
        '''

        :return: values, times

        '''

        return self.temperature

    def getrawVoltage(self) -> tuple[str, str]:
        '''

        :return: values, times
        '''
        return self.voltage

    def getVoltage(self):

        values, dates = self.getdataModified(self.getrawVoltage())

        return values, dates

    def getdataModified(self, data) -> (tuple[str, str], tuple[float, datetime]):  # get data with daily average and rolling mean

        '''

        :param tuple[str, str] data:  values, times
        :return: Rolling mean of an average values filtered by timestamp

        '''
        values = data[1]
        times = data[0]
        # if the devices not communicating the values are false
        if values is False:

            self.error = 'ne communique pas'

            return values, times
        else:
            self.error = 'communique'
            # suppressing de the values between 6:00 AM  9:00 PM and the values bellow 10V
            values, dates = getFilterValues(values, getDate(times))
            # doing a daily average
            values, times = getAverage(values, getTime(dates))
            # kheiron give us a timestamp with an offset, rescaling timestamp
            realtime = getGoodTimestamp(times)
            realdate = getDate(realtime)
            # doing a rolling mean
            #values = getRollingMean(values, self.step)

            return values, realdate

    def _currentanomaly(self) -> bool:

        temperature, temptimes = self.getdataModified(self.getrawTemperature())
        current, currenttime = self.getdataModified(self.getrawTemperature())

        tempdeviation = 0.35  # step percentage for temperature
        currdeviation = 0.10  # step percentage for current

        # we check if device communicating or not
        if current is not False:

            for i in range(self.step, len(temperature) - 1):
                # getting a percentage of the value to identify the step
                bsuptemp = temperature[i] + (temperature[i] * tempdeviation)
                binftemp = temperature[i] - (temperature[i] * tempdeviation)
                # finding the step
                if temperature[i + 1] >= bsuptemp or temperature[i + 1] <= binftemp:
                    # same but for current
                    bsupcurr = current[i] + (current[i] * currdeviation)
                    binfcurr = current[i] + (current[i] * currdeviation)

                    if current[i + 1] >= bsupcurr or current[i + 1] <= binfcurr:
                        return True
        else:
            return False

        return False

    def _oldceramics(self) -> bool:
        sixmonthonseconds = 15552000
        values, times = self.getcptCeramique()
        cpt = values[len(values) - 1]  # get the last value in second
        if int(cpt) >= sixmonthonseconds:
            return True
        else:
            return False

    def _tendency(self) -> (tuple[bool, str], tuple[bool, bool]):  # tendency algo

        voltage, dates = self.getdataModified(self.getrawVoltage())
        voltagestart = 0
        cpt = 0
        nbjours = 3
        borne = 7.5
        binf = 0  # self.step  # rolling mean step
        bsup = 5  # binf + 8

        if self.error == 'ne communique pas':
            return False, self.error

        if bsup > len(voltage):
            error = 'manque de donnees'

            return False, error

        else:
            # finding 7.5 V step during 3 days
            for i in range(0, len(voltage)-3):
                if abs(voltage[i] - voltage[i + 1]) >= borne:
                    if abs(voltage[i] - voltage[i + 2]) >= borne:
                        if abs(voltage[i] - voltage[i + 3]) >= borne:
                            return True, dates[i]


            return False, 'RAS'

    def _worksoncermic(self) -> (tuple[bool, bool], tuple[bool, str]):  # finding a works on ceramic
        values, times = self.getcptCeramique()
        for i in range(0, len(values)):
            if values[i] == '0':
                return True, times[i]

        return False, False

    def _stdincrease(self,
                     workstime) -> bool:  # search for an increase in standard deviation in the days following or preceding

        voltage = self.getrawVoltage()
        values = voltage[1]
        times = voltage[0]
        worksdate = datetime.fromtimestamp(workstime)
        stdvalues, stddate = getdailystd(values, times)  # get daily standard deviation

        for i in range(1, len(stdvalues) - 1):
            if stddate[i - 1] < worksdate < stddate[i + 1] and (stdvalues[i - 1] - stdvalues[i + 1]) > 0:
                return True
            else:
                return False

    def _indicator(self):  # different indicator with breakdown probability
        probability = 0
        date = '-'
        tendency, err = self._tendency()
        if tendency:
            probability = 62
            date = err
            err = 'aucune'
            breakdowndate = date + relativedelta(days=31)
            worksonceramic, workstime = self._worksoncermic()
            if worksonceramic:
                stdincrease = self._stdincrease(workstime)
                if stdincrease:
                    probability = 90
                    data = [self.getName(), breakdowndate, probability, self.getGeographicZone(), err]
                    return data
                else:
                    data = [self.getName(), breakdowndate, probability, self.getGeographicZone(), err]
                    return data

            else:
                currentanomaly = self._currentanomaly()
                oldceramics = self._oldceramics()
                if currentanomaly or oldceramics:
                    probability = 80
                    data = [self.getName(), breakdowndate, probability, self.getGeographicZone(), err]
                    return data
                else:
                    data = [self.getName(), breakdowndate, probability, self.getGeographicZone(), err]
                    return data

        else:

            data = [self.getName(), date, probability, self.getGeographicZone(), err]
            return data
