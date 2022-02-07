import json
import urllib.parse
import http.client
from datetime import datetime
from lib import debug, getStartTime, debug2


class Connect(object):

    def __init__(self):
        self.connection = http.client.HTTPSConnection("api.kheiron-sp.io", 443)
        self.username = 'a.tortevois@areco.fr'
        self.password = '@recO06130'
        self.tokenexpiry = False
        self.devicesJson = False
        self.token = self._getToken()
        self.contractsId = self._getContractsId()
        self.devices = self._getDevices()
        self.tagsValue = self._getTagsValue()
        self.nebulecolist = self._getNebuleco()

    def getGeographicZone(self, id) -> str:
        '''

        :param str id: identifier of nébuleco
        :return:  nébuleco localisation
        '''
        for device in self.devices:
            if device['id'] == id:
                return device['details']

    def getNebulecoList(self):
        return self.nebulecolist

    def getId(self, name):
        for device in self.devices:
            tmp_name = device['name']
            if name == tmp_name:
                return device['id']

    def getDayExpiresToken(self):
        return self.tokenexpiry

    def getToken(self):
        return self.token

    def getContractsId(self):
        return self.contractsId

    def getDevices(self):
        return self.devices

    def getLastLog(self, nameValue, idDevice):

        try:

            tag = self.tagsValue[nameValue]

        except KeyError:

            return False
        payload = ''
        headers = {'Authorization': 'Bearer ' + self.getToken()}
        # GET historic voltage devices
        self.connection.request("GET",
                                "/v1/devices/realtimes" + "?contractId=" + self.getContractsId() + "&deviceId=" + idDevice + '&tagReferences=' + tag,
                                payload, headers)  # +'&tagReferences='+tagReference
        res = self.connection.getresponse()
        historicsbytes = res.read()
        # Saving historic Voltage
        historicValuesJson = json.loads(historicsbytes.decode("utf8"))
        historicValues = historicValuesJson['logs']
        timestamp = historicValues[0]['timestamp']
        # timestamp=historicValues['timestamp']
        date = datetime.fromtimestamp(timestamp)

        return date

    def _getToken(self):
        name = urllib.parse.quote(self.username)
        Pass = urllib.parse.quote(self.password)

        ## Log in ##
        payload = 'grant_type=password&username=' + name + '&password=' + Pass
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        ## requesting token ##
        self.connection.request("POST", "/token", payload, headers)

        ## Save token ##
        result = self.connection.getresponse()
        tokenBytes = result.read()
        tokenJson = json.loads(tokenBytes.decode("utf-8"))
        token = tokenJson['access_token']
        tokenexpires = tokenJson['.expires']
        tmp = tokenexpires.split(' ')
        self.tokenexpiry = int(tmp[1])
        debug("token : success")

        return token

    def _getContractsId(self) -> dict:
        '''

        :return: contracts id from kheiron API
        '''
        payload = ''
        headers = {'Authorization': 'Bearer ' + self.getToken()}

        ## setup URL ##
        self.connection.request("GET", "/v1/contracts", payload, headers)

        ## request get for contracts ##
        result = self.connection.getresponse()
        contractsBytes = result.read()
        contractsJson = json.loads(contractsBytes.decode("utf8"))
        listContracts = contractsJson['contracts']

        ## get Contracts ID ##
        dictContracts = listContracts[0]
        contractsId = dictContracts["id"]
        debug("contractsId : success")

        return contractsId

    def _getDevices(self):

        payload = ''
        headers = {'Authorization': 'Bearer ' + self.getToken()}
        ## setup URL ##
        self.connection.request("GET", "/v1/devices?contractId=" + self.getContractsId(), payload, headers)
        ## requesting devices ##
        result = self.connection.getresponse()
        devicesBytes = result.read()
        ## save devices ##
        devicesJson = json.loads(devicesBytes.decode("utf8"))
        devicesList = devicesJson['devices']
        print("devices : success")

        return devicesList

    def getValue(self, namevalue, lastlog, deviceid, minusmonth):

        values = []
        times = []
        tag = self.tagsValue[namevalue]
        startTime = getStartTime(lastlog, minusmonth)
        payload = ''
        headers = {'Authorization': 'Bearer ' + self.getToken()}
        ## GET historic values devices ##s
        self.connection.request("GET",
                                "/v1/devices/historics" + "?contractId=" + self.getContractsId() + "&deviceId=" + deviceid + "&startTime="+startTime +"&tagReferences="+tag,
                                payload, headers)  # +'&tagReferences='+tagReference
        res = self.connection.getresponse()
        historicBytes = res.read()
        ## Saving historic values ##
        debug2(f'historic = {historicBytes} , starttime = {startTime}, tagref = {tag}')
        debug(f'start time={startTime}')
        historicValuesJson = json.loads(historicBytes.decode("utf8"))
        historicValues = historicValuesJson['historics']
        try:
            logsValuesList = historicValues[0]['logs']
            for log in logsValuesList:

                values.append(log['value'])
                times.append(log['timestamp'])
        except IndexError:
            tmp = [False, False]
            return tmp

        tmp = [times, values]
        return tmp

    def _getNebuleco(self):

        names = []

        for device in self.devices:
            name = device["name"]
            tmp = name.split('.')[0]
            if tmp == 'NEB':
                names.append(name)

        return names

    def _getTagsValue(self):

        tagsValues = dict()

        tagsValues['FLAGNEBU'] = 'r_0'
        tagsValues['TASKNEBU'] = 'r_1'
        tagsValues['FLAGCHAUF'] = 'r_2'
        tagsValues['FLAGNIVEAU'] = 'r_3'
        tagsValues['FLAGVIDANG'] = 'r_4'
        tagsValues['BOARDVOL'] = 'r_5'
        tagsValues['TEMPE'] = 'r_6'
        tagsValues['CURRENTPIEZO'] = 'r_7'
        tagsValues['TENSIONPIEZO'] = 'r_8'
        tagsValues['FREQPOMPE'] = 'r_9'
        tagsValues['TASKCHAUF'] = 'r_10'
        tagsValues['TASKVIDANGE'] = 'r_11'
        tagsValues['TASKBUZZER'] = 'r_12'
        tagsValues['HR'] = 'r_13'
        tagsValues['HRMIN'] = 'r_14'
        tagsValues['HRMAX'] = 'r_15'
        tagsValues['DC'] = 'r_16'
        tagsValues['DCMIN'] = 'r_17'
        tagsValues['DCMAX'] = 'r_18'
        tagsValues['HORMONAL'] = 'r_19'
        tagsValues['DCMOYPARJOUR'] = 'r_20'
        tagsValues['CURRTHERMO'] = 'r_21'
        tagsValues['ACTIVETHERMO'] = 'r_22'
        tagsValues['PILERTC'] = 'r_23'
        tagsValues['CURRVENTIL'] = 'r_24'
        tagsValues['FREQPIEZO'] = 'w_0'
        tagsValues['DELAIPIEZO'] = 'w_1'
        tagsValues['PASFREQ'] = 'w_2'
        tagsValues['FPWM'] = 'w_3'
        tagsValues['PWMNEBU'] = 'w_4'
        tagsValues['PWMVENTIL'] = 'w_5'
        tagsValues['PWMPOMPE'] = 'w_6'
        tagsValues['RAPC'] = 'w_7'
        tagsValues['VALIDNEBU'] = 'w_8'
        tagsValues['VALIDCHAF'] = 'w_9'
        tagsValues['RECHFREQ'] = 'w_10'
        tagsValues['SHUNTERR'] = 'w_11'
        tagsValues['CONSCURRENT'] = 'w_12'
        tagsValues['ERRCURMIN'] = 'w_13'
        tagsValues['ERRCURMAX'] = 'w_14'
        tagsValues['CONSTEMPCH'] = 'w_15'
        tagsValues['ERRTEMPMAX'] = 'w_16'
        tagsValues['FREQPUMP'] = 'w_17'
        tagsValues['VOLMAX'] = 'w_18'
        tagsValues['FREQPUMPST'] = 'w_19'
        tagsValues['MAT'] = 'w_20'
        tagsValues['BUZZER'] = 'w_21'
        tagsValues['POTAR'] = 'w_22'
        tagsValues['ASSERV'] = 'w_23'
        tagsValues['DIVRC'] = 'w_24'
        tagsValues['CHGTHEURE'] = 'w_25'
        tagsValues['REGUL'] = 'w_26'
        tagsValues['CONSIGNHR'] = 'w_27'
        tagsValues['G'] = 'w_28'
        tagsValues['TI'] = 'w_29'
        tagsValues['TD'] = 'w_30'
        tagsValues['VALIDPRELEV'] = 'w_31'
        tagsValues['DELTAHR'] = 'w_32'
        tagsValues['SECUHRSEUILBAS'] = 'w_33'
        tagsValues['CONSHRMAX'] = 'w_34'
        tagsValues['TYPEVENTILO'] = 'w_35'
        tagsValues['PWMVENTILMIN'] = 'w_36'
        tagsValues['TYPESONDE'] = 'w_37'
        tagsValues['NUMGAINA'] = 'w_38'
        tagsValues['DENOMGAINB'] = 'w_39'
        tagsValues['OFFSETC'] = 'w_40'
        tagsValues['CHAUFFEDEM'] = 'w_41'
        tagsValues['CONSTENMAX'] = 'w_42'
        tagsValues['CONSCURRMIN'] = 'w_43'
        tagsValues['CONSCURRMAX'] = 'w_44'
        tagsValues['FREQPOMPMIN'] = 'w_45'
        tagsValues['CONTROLTEMPE'] = 'w_46'
        tagsValues['ERRTEMPEMIN'] = 'w_47'
        tagsValues['SERVO'] = 'w_48'
        tagsValues['MODEEXPERT'] = 'w_49'
        tagsValues['RCSONDESATU'] = 'w_50'
        tagsValues['MANQUE_EAU'] = 'err_1'
        tagsValues['VIDANGE'] = 'err_2'
        tagsValues['CHAUFFE_NC'] = 'err_3'
        tagsValues['CHAUFFE_SS_EAU'] = 'err_4'
        tagsValues['TEMPERATURE'] = 'err_5'
        tagsValues['FLOTTEUR'] = 'err_6'
        tagsValues['CERAMIQUE_DEB'] = 'err_7'
        tagsValues['CALAGE_CER'] = 'err_8'
        tagsValues['24V'] = 'err_9'
        tagsValues['12V'] = 'err_10'
        tagsValues['POMPE'] = 'err_11'
        tagsValues['SONDE_DEBR'] = 'err_12'
        tagsValues['SONDE_SAT'] = 'err_13'
        tagsValues['SONDE_TEMP_DEB'] = 'err_14'
        tagsValues['RESISTANCE_HS'] = 'err_15'
        tagsValues['COMPTEUR_CERAMQIUE'] = 'tf_1'

        return tagsValues
