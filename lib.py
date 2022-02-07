







from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas import DataFrame
import pandas as pd
import numpy as np
import re
import xlsxwriter

DEBUG = False
DEBUG2 = False

def getshutingvoltage(date):
    a = date - relativedelta(months=1)

    return a
def debug2(message):
    if DEBUG2: print(f'{message}')

def suppchar(zone):
    zone.replace('é', 'e')
    return zone


def color_font(v):
    date = datetime.now()
    print(v)
    tmp = v - date
    print(tmp)
    d = tmp.days
    if 1<=d<=5:
        return 'color: white;background-color:red'
    if 5<d<=16:
        return 'color: white;background-color:orange'
    if d>16:
        return 'color: white;background-color:green'





def getdailystd(values, times):

    stDate = []
    stValue = []
    dValues = []
    date = getDate(times)
    t1 = 0
    flag = 0
    cpt = 0
    for i in range(0, len(values)):
        if flag == 0:
            t1 = date[i].day
            flag = 1
        t2 = date[i].day
        dValues.append(int(values[i]))
        cpt += 1
        if t1 - t2 != 0:
            stDate.append(date[i])
            stValue.append(np.std(dValues))
            dValues = []
            flag = 0
            cpt = 0

    return stValue, stDate

def findzero(values):

    for value in values:
        if int(value) == 0:
            return True
    return False

def getStartTime(lastLogDate, minusMonth):
    startDate = datetime.fromtimestamp(lastLogDate) - relativedelta(months=minusMonth)

    debug(f'start date : {startDate} \nlast log date : {lastLogDate}\n')
    startTime = str(int(datetime.timestamp(startDate)))
    return startTime

def setdataexcel(dataName, dataBreak, dataProba, dataLoc, dataError) :

    c_ras = {
        'Nom': [],
        'Localisation': [],
    }
    c_none = {
        'Nom': [],
        'Localisation': [],
    }
    c_breakdown = {
        'Nom': [],
        'Localisation': [],
        'Proba%': [],
        'Date': [],

    }

    c_lackdata = {
        'Nom': [],
        'Localisation': [],
    }
    # setting data for different sheet
    for i in range(0, len(dataError)):

        if dataError[i] == 'RAS':
            c_ras['Nom'].append(dataName[i])
            c_ras['Localisation'].append(dataLoc[i])
        elif dataError[i] == 'aucune':
            c_breakdown['Nom'].append(dataName[i])
            c_breakdown['Localisation'].append(dataLoc[i])
            c_breakdown['Date'].append(dataBreak[i])
            c_breakdown['Proba%'].append(dataProba[i])
        elif dataError[i] == 'manque de donnees':
            c_lackdata['Nom'].append(dataName[i])
            c_lackdata['Localisation'].append(dataLoc[i])
        else:
            c_none['Nom'].append(dataName[i])
            c_none['Localisation'].append(dataLoc[i])
    return c_breakdown, c_none, c_lackdata, c_ras

def excelwriter(title, dataName, dataBreak, dataProba, dataLoc, dataError) :

    regex = re.compile(r'[\n\t\r]')
    path = title+'.xlsx'
    c_breakdown, c_none, c_lackdata, c_ras = setdataexcel(dataName, dataBreak, dataProba, dataLoc, dataError)
    # create dataframe
    datalack = DataFrame(c_lackdata, columns=['Nom', 'Localisation'])
    datab = DataFrame(c_breakdown, columns=['Nom', 'Date', 'Proba%', 'Localisation'])
    datanone = DataFrame(c_none, columns=['Nom', 'Localisation'])
    dataras = DataFrame(c_ras, columns=['Nom', 'Localisation'])
    # sort dataframe
    datalack = datalack.sort_values(by=['Localisation'], ascending=True)
    datab = datab.sort_values(by=['Date', 'Localisation'], ascending=True)
    datanone = datanone.sort_values(by=['Localisation'], ascending=True)
    dataras = dataras.sort_values(by=['Localisation'], ascending=True)
    # create the file and path writer
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    # writing data on excel
    slice_ = ['Date']
    datab = datab.style.applymap(color_font, subset=slice_)
    datab.to_excel(writer, sheet_name='Pannes', freeze_panes=(1, 1))
    datanone.to_excel(writer, sheet_name='Ne communique pas', freeze_panes=(1, 1))
    datalack.to_excel(writer, sheet_name='Manque de data', freeze_panes=(1, 1))
    dataras.to_excel(writer, sheet_name='RAS', freeze_panes=(1, 1))
    writer.save()
    writer.close()

def csvwriter(title, dataName, dataBreak, dataProba, dataLoc, dataError):
    regex = re.compile(r'[\n\t\r]')

    C = {'Nom': dataName,
         'Date Panne': dataBreak,
         'Proba%': dataProba,
         'Localisation': dataLoc,
         'Erreur': dataError,
         }
    data = DataFrame(C, columns=['Nom', 'Date Panne', 'Proba%', 'Localisation', 'Erreur'])
    for i in data.index:
        tmp = data['Localisation'][i]
        tmp = tmp.replace('è', 'e')
        tmp = tmp.replace('é', 'e')
        tmp = tmp.replace('ü', 'u')
        tmp = regex.sub(":", tmp)
        if tmp.split('::')[0] == 'OMF Servon':
            tmp = 'OMF Servon'
        data['Localisation'][i] = tmp
    for i in data.index:
        tmp = data['Localisation'][i]
        tmp = tmp.replace('::', '')
        print(tmp)
        data['Localisation'][i] = tmp

    sorteddata = data.sort_values(by=['Date Panne', 'Proba%', 'Erreur', 'Localisation'], ascending=True)
    sorteddata.to_csv(title + '.csv', index=False, header=True, encoding='utf-8', sep=';')


def getTime(date):
    times = []

    for d in date:
        if d is False:
            return False

    for dat in date:
        times.append(datetime.timestamp(dat))
    return times


def getGoodTimestamp(times):
    goodtime = []
    for t in times:
        if t is False:
            return False
    else:
        for t in times:
            goodtime.append(t + 946677572)
    return goodtime


def getRollingMean(values, step):

    data = np.array(values)
    d = pd.Series(data)
    rValues = d.rolling(step).mean()
    return rValues


def getDate(aTime):
    if aTime is False:
        return False
    else:
        aDate = []
        for a in aTime:
            d = datetime.fromtimestamp(a)
            aDate.append(d)
        return aDate


def getFilterValues(values, date):
    fValues = []
    fDate = []
    bInf = 8
    bSup = 19
    for i in range(0, len(date)):
        if bInf < date[i].hour < bSup and int(values[i])>15:

            fDate.append(date[i])
            fValues.append(values[i])
    return fValues, fDate


def getAverage(values, times):
    aTime = []
    aVoltage = []
    date = getDate(times)
    t1 = 0
    flag = 0
    cpt = 0
    summa = 0
    for i in range(0, len(values)):
        if flag == 0:
            t1 = date[i].day
            flag = 1
        t2 = date[i].day
        summa += float(values[i])
        cpt += 1
        if t1 - t2 != 0:
            tmp = (summa-float(values[i])) / (cpt-1)
            aVoltage.append(tmp)
            aTime.append(times[i-1])
            flag = 0
            cpt = 0
            summa = 0

    return aVoltage, aTime

def debug(message):
    if DEBUG: print(f'{message}')
