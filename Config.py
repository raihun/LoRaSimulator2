# -*- encoding:utf-8 -*-
from configparser import ConfigParser
from os.path import exists


class Config:
    """ config.ini Read/Write用 クラス """
    __filename = "config.ini"

    def __init__(self):
        self.__readConfig()
        return

    def getSimulator(self):
        simulator = Config.__config["General"]["Simulator"]
        if simulator == "":
            simulator = "false"
        return simulator

    def getDevicename(self):
        devicename = Config.__config["Device"]["Name"]
        if devicename == "":
            devicename = "/dev/tty.USB0"
        return devicename

    def getBaudrate(self):
        baudrate = Config.__config["Device"]["Baudrate"]
        if baudrate == "":
            baudrate = "9600"
        return baudrate

    def getBandwidth(self):
        bandwidth = Config.__config["LoRa"]["Bandwidth"]
        if bandwidth == "":
            bandwidth = "4"  # 3, 4, 5, 6
        return bandwidth

    def getSpreadingfactor(self):
        spreadingfactor = Config.__config["LoRa"]["Spreadingfactor"]
        if spreadingfactor == "":
            spreadingfactor = "7"  # 7-12
        return spreadingfactor

    def getChannel(self):
        channel = Config.__config["LoRa"]["Channel"]
        if channel == "":
            channel = "1"
        return channel

    def getPanid(self):
        panid = Config.__config["LoRa"]["Panid"]
        if panid == "":
            panid = "0001"
        return panid

    def setOwnid(self, param):
        Config.__config["LoRa"]["Ownid"] = param
        return

    def getOwnid(self):
        ownid = Config.__config["LoRa"]["Ownid"]
        if ownid == "":
            ownid = "0001"
        return ownid

    def getPower(self):
        power = Config.__config["LoRa"]["Power"]
        if power == "":
            power = "13"
        return power

    def getHost(self):
        host = Config.__config["Simulator"]["Host"]
        if host == "":
            host = "127.0.0.1"
        return host

    def getPort(self):
        host = Config.__config["Simulator"]["Port"]
        if host == "":
            host = "25561"
        return host

    def getSimulatorDebug(self):
        debug = Config.__config["Simulator"]["Debug"]
        if debug == "":
            debug = "false"
        return debug

    """ コンフィグファイル 読込 """
    def __readConfig(self):
        # 初回インスタンス化チェック
        try:
            if Config.__isFisrtread:
                return
        except AttributeError:
            Config.__isFisrtread = True

        # 設定読み込み
        Config.__config = ConfigParser()

        if not exists(self.__filename):
            # General
            Config.__config["General"] = {}
            Config.__config["General"]["Simulator"] = "false"

            # Device setting
            Config.__config["Device"] = {}
            Config.__config["Device"]["Name"] = "/dev/tty.USB0"
            Config.__config["Device"]["Baudrate"] = "9600"

            # LoRa setting
            Config.__config["LoRa"] = {}
            Config.__config["LoRa"]["Bandwidth"] = "4"  # 3, 4:125kHz, 5, 6
            Config.__config["LoRa"]["Spreadingfactor"] = "7"  # 7-12
            Config.__config["LoRa"]["Channel"] = "1"
            Config.__config["LoRa"]["Panid"] = "0001"
            Config.__config["LoRa"]["Ownid"] = "0001"
            Config.__config["LoRa"]["Power"] = "13"  # Min:-4 to Max:13

            # Simulator setting
            Config.__config["Simulator"] = {}
            Config.__config["Simulator"]["Host"] = "127.0.0.1"
            Config.__config["Simulator"]["Port"] = "25561"
            Config.__config["Simulator"]["Debug"] = "false"

            # Create config file
            self.__writeConfig()
        Config.__config.read(self.__filename)
        return

    """ コンフィグファイル 書出 """
    def __writeConfig(self):
        with open(self.__filename, "w") as fp:
            Config.__config.write(fp)
        return
