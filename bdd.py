import cx_Oracle
import pandas
import pandas as pd

cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle\instantclient_21_3")


class Bdd_neb:
    def __init__(self, user, password, dsn):
        self.connection = cx_Oracle.connect(
            user=user,
            password=password,
            dsn=dsn
        )
        self.cursor = self.connection.cursor()
        self.tagsValue = self._getTagsValue()

    def getId(self):
        select = "select id_device from devices"
        self.cursor.execute(select)
        df = pandas.DataFrame(self.cursor.fetchall())
        df.columns = ['id']

        return df['id']

    def getFromVariables(self, id_neb, tag_value):
        id_device = int(id_neb)
        select = "select value,v_date,vartag from variables where id_device = "+ str(id_device) #+ " and vartag =" + vartag  #+ str(self.tagsValue[tag_value])
        self.cursor.execute(select)
        df = pandas.DataFrame(self.cursor.fetchall())
        print(df)
        try:
            df.columns = ['value', 'date', 'vartag']
        except ValueError:
            df = pd.DataFrame(data={'value': [0], 'date': [0]})
            return df
        print(df["value"])
        tmp = df[df['vartag']==self.tagsValue[tag_value]]   #tmp = df.filter(items='r_7', axis='columns')
        return tmp

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
