# -*- encoding:utf-8 -*-
import configparser
import os.path


class Config:
    filename = "config.ini"

    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__readConfig()
        return

    def __readConfig(self):
        if(not os.path.exists("config.ini")):
            # Device setting
            self.__config["Device"] = {}
            self.__config["Device"]["Name"] = "/dev/tty.USB0"
            self.__config["Device"]["Baudrate"] = "9600"

            # LoRa setting
            self.__config["LoRa"] = {}
            self.__config["LoRa"]["Bandwidth"] = "4"  # 4:125kHz
            self.__config["LoRa"]["Spreadingfactor"] = "12"
            self.__config["LoRa"]["Channel"] = "1"
            self.__config["LoRa"]["Panid"] = "0001"
            self.__config["LoRa"]["Ownid"] = "0001"
            self.__config["LoRa"]["Power"] = "13"  # Min:-4 to Max:13

            # Create config file
            self.__writeConfig()
        self.__config.read(self.filename)
        return

    def __writeConfig(self):
        with open(self.filename, "w") as fp:
            self.__config.write(fp)
        return

    def getDevicename(self):
        devicename = self.__config["Device"]["Name"]
        if(devicename == ""):
            devicename = "/dev/tty.USB0"
        return devicename

    def getBaudrate(self):
        baudrate = self.__config["Device"]["Baudrate"]
        if(baudrate == ""):
            baudrate = "9600"
        return baudrate

    def getBandwidth(self):
        bandwidth = self.__config["LoRa"]["Bandwidth"]
        if(bandwidth == ""):
            bandwidth = "4"
        return bandwidth

    def getSpreadingfactor(self):
        spreadingfactor = self.__config["LoRa"]["Spreadingfactor"]
        if(spreadingfactor == ""):
            spreadingfactor = "7"  # 7-12
        return spreadingfactor

    def getChannel(self):
        channel = self.__config["LoRa"]["Channel"]
        if(channel == ""):
            channel = "1"
        return channel

    def getPanid(self):
        panid = self.__config["LoRa"]["Channel"]
        if(panid == ""):
            panid = "0001"
        return panid

    def getOwnid(self):
        ownid = self.__config["LoRa"]["Ownid"]
        if(ownid == ""):
            ownid = "0001"
        return ownid

    def getPower(self):
        power = self.__config["LoRa"]["Power"]
        if(power == ""):
            power = "13"
        return power
