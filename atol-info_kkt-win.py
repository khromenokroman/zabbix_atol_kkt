from libfptr10 import IFptr
import sys
import os
import codecs
import datetime

PATH = r'C:\\ATOL\\ATOL_INFO_KKT'
COMMANDS = ['fn_end','fn_ofd_status'] #список всех команд

def get_delta_day(date_fn):# узнаем сколько дней до окнчания срока действия фн
    
    date_now = datetime.datetime.now() #текущая дата
    # date_fn = datetime.datetime.strptime(date_fn_str, '%Y-%m-%d %H:%M:%S') #строку в дату

    delta = date_fn - date_now #разница
    if delta.days >= 0:
        return delta.days #вывод
    else:
        return 'Ошибка'

def get_status_ofd(date_fn):# узнаем сколько дней назад был успешный обмен с офд
    
    date_now = datetime.datetime.now() #текущая дата
    # date_fn = datetime.datetime.strptime(date_fn_str, '%Y-%m-%d %H:%M:%S') #строку в дату

    delta = date_now - date_fn #разница
    
    if delta.days >= 0:
        return delta.days #вывод
    else:
        return 'Ошибка'

def get_indo_kkt(command):

    
    fptr = IFptr(f'{PATH}\\fptr10.dll')
    
    version = fptr.version() #Версия ДТО
    
    #подключаемся к кассе
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_MODEL, str(IFptr.LIBFPTR_MODEL_ATOL_AUTO))
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_USB))
    res=fptr.applySingleSettings()
    fptr.open()
    isOpened = fptr.isOpened()

    if isOpened==0: #если не прошло пытаемся по COM
        fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_MODEL, str(IFptr.LIBFPTR_MODEL_ATOL_AUTO))
        # fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_USB))
        fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_COM))
        fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_COM_FILE, "COM1")
        fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_BAUDRATE, str(IFptr.LIBFPTR_PORT_BR_115200))
        res=fptr.applySingleSettings()
        fptr.open()
        isOpened = fptr.isOpened()

    if isOpened != 0:

        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_STATUS)
        fptr.queryData()
        serialNumber    = fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER) #Номер ФР
        modelName       = fptr.getParamString(IFptr.LIBFPTR_PARAM_MODEL_NAME) #Модель ФР
        firmwareVersion = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION) #Прошивка
        smena = fptr.getParamString(IFptr.LIBFPTR_PARAM_SHIFT_STATE) # 0 = Смена закрыта, 1=Смена открыта
        numberCheck = fptr.getParamString(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER) #Номер чека
        dateTimeFr = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME) #Время ФР

        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
        fptr.fnQueryData()
        organizationName            = fptr.getParamString(1048) #Организация
        ffdVersion                  = fptr.getParamInt(1209) #Версия ФФД
        ofdVATIN                    = fptr.getParamString(1017) #ИНН ОФД
        adress_mag                  = fptr.getParamString(1009) #Адрес магазина
        ofdName                     = fptr.getParamString(1046) #ОФД
        regNumberFN                 = fptr.getParamString(1037) #Регномер ФН

        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_FN_INFO)
        fptr.fnQueryData()

        fnSerial            = fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER) #Номер ФН
        fnExhausted         = fptr.getParamBool(IFptr.LIBFPTR_PARAM_FN_RESOURCE_EXHAUSTED) #Исчерпан ресурс ФН
        fnMemoryOverflow    = fptr.getParamBool(IFptr.LIBFPTR_PARAM_FN_MEMORY_OVERFLOW) #Пямять ФН переполнена
        fnOfdTimeout        = fptr.getParamBool(IFptr.LIBFPTR_PARAM_FN_OFD_TIMEOUT)
        fnCriticalError     = fptr.getParamBool(IFptr.LIBFPTR_PARAM_FN_CRITICAL_ERROR) #Критическая ошибка ФН

        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_OFD_EXCHANGE_STATUS)
        fptr.fnQueryData()

        exchangeStatus      = fptr.getParamInt(IFptr.LIBFPTR_PARAM_OFD_EXCHANGE_STATUS) #0=соединение установлено, 1=есть сообщение для передачи в ОФД, 
        #2=ожидание ответного сообщения от ОФД, 3=есть команда от ОФД, 4=изменились настройки соединения с ОФД, 5=ожидание ответа на команду от ОФД
        unsentCount         = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENTS_COUNT) #Количество неотправленных чеков
        firstUnsentNumber   = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER) #Номер первого неотправленного документа
        ofdMessageRead      = fptr.getParamBool(IFptr.LIBFPTR_PARAM_OFD_MESSAGE_READ) #Флаг наличия сообщения для ОФД
        dateTimeFn            = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME) #Первый неотправленный документ

        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_LAST_SENT_OFD_DOCUMENT_DATE_TIME)
        fptr.queryData()
        dateTimeOfd = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME) #Последний успешный обмен с ОФД

        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_VALIDITY)
        fptr.fnQueryData()
        dateTimeFnEnd            = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME) #Дата окончания ФН

        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_ERRORS)
        fptr.fnQueryData()
        networkErrorText    = fptr.getParamString(IFptr.LIBFPTR_PARAM_NETWORK_ERROR_TEXT) #Ошибка сети
        ofdErrorText        = fptr.getParamString(IFptr.LIBFPTR_PARAM_OFD_ERROR_TEXT) #Ошибка ОФД
        fnErrorText         = fptr.getParamString(IFptr.LIBFPTR_PARAM_FN_ERROR_TEXT) #Ошибка ФН

        #считать даные ОФД
        fptr.setParam(IFptr.LIBFPTR_PARAM_SETTING_ID, 273)
        fptr.readDeviceSetting()
        settingValue = fptr.getParamString(IFptr.LIBFPTR_PARAM_SETTING_VALUE) #Адрес ОФД
        fptr.setParam(IFptr.LIBFPTR_PARAM_SETTING_ID, 274)
        fptr.readDeviceSetting()
        settingValue = fptr.getParamString(IFptr.LIBFPTR_PARAM_SETTING_VALUE) #Порт ОФД
        fptr.setParam(IFptr.LIBFPTR_PARAM_SETTING_ID, 276)
        fptr.readDeviceSetting()
        settingValue = fptr.getParamString(IFptr.LIBFPTR_PARAM_SETTING_VALUE) #1=EoU, 2=Ethernet, 5=EoT
        fptr.setParam(IFptr.LIBFPTR_PARAM_SETTING_ID, 239)
        fptr.readDeviceSetting()
        settingValue = fptr.getParamString(IFptr.LIBFPTR_PARAM_SETTING_VALUE) #0=COM, 4=USB
        
        fptr.close()
        del fptr

        if command == 'fn_end':
            return get_delta_day(dateTimeFnEnd)
        elif command == 'fn_ofd_status':
            return get_status_ofd(dateTimeOfd)
    else:
        return 'device is not connected...'

if __name__ == '__main__':

    # for item in COMMANDS:
    #     if item == sys.argv[1]:
    #         print(get_indo_kkt(sys.argv[1]))
    #     else:
    #         print('incomprehensible command')
    if sys.argv[1] not in COMMANDS:
        print('incomprehensible command')
    else:
        print(get_indo_kkt(sys.argv[1]))