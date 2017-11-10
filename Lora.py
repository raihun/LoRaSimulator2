# -*- encoding:utf-8 -*-
import serial
import threading
import Config


class Lora:
    def __init__(self):
        self.config = Config.Config()
        self.__connect()
        return

    def __connect(self):
        devicename = self.config.getDevicename()
        baudrate = self.config.getBaudrate()

        try:
            self.__device = serial.Serial(devicename, int(baudrate))
        except Exception as e:
            print(e)
            return

        # Receive thread
        self.__thRecv = threading.Thread(
            target=self.__recvThread,
            args=(None, self.__device)
        )
        self.__thRecv.setDaemon(True)
        self.__thRecv.start()

        # Send thread
        self.__thSend = threading.Thread(
            target=self.__sendThread,
            args=(None, self.__device)
        )
        self.__thSend.setDaemon(True)
        self.__thSend.start()
        return

    def __setting(self):
        return

    def __send(self, rawdata):
        return

    def __recv(self):
        return

    @staticmethod
    def __recvThread(self, device):
        print("Start recv thread.")
        while True:
            if(device.inWaiting() > 0):
                try:
                    line = device.readline().decode('utf-8')
                except UnicodeDecodeError:
                    continue
                print(line, end='')
        return

    @staticmethod
    def __sendThread(self, device):
        while True:
            cmd = input()
            cmd = "{0}\r\n".format(cmd).encode()
            device.write(cmd)
        return
