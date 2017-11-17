# -*- encoding:utf-8 -*-
from Config import Config
import socket
import sys


class Simulator:
    """
        このクラスでは、ES920LRのシミュレータを作成する
    """
    def __init__(self, devicename, baudrate):
        self.__config = Config()
        self.__isStart = False
        return

    def write(self, rawdata):
        data = rawdata.decode('utf-8').strip()
        if(not self.__isStart):
            self.__modeConfig(data)
        else:
            self.__modeStart(data)
        return

    def inWaiting(self):
        if(not self.__isStart):
            return 0
        try:
            self.recvmsg = self.sock.recv(4096).decode().strip()
        except ConnectionResetError:  # サーバ側からの切断
            self.sock.close()
        except OSError:  # サーバダウン
            print("[Error] サーバダウン")
            self.sock.close()
            sys.exit()

        if(len(self.recvmsg) <= 0):
            self.sock.close()
        return len(self.recvmsg)

    def readline(self):
        return self.recvmsg.encode()

    def __modeConfig(self, data):
        # Split command
        data = data.split(" ")
        c = data[0]
        if(len(data) > 1):
            m = data[1]

        # Set parameters
        if(c is "b"):  # bw
            self.__bw = int(m)
        if(c is "c"):  # sf
            self.__sf = int(m)
        if(c is "d"):  # channel
            self.__ch = int(m)
        if(c is "e"):  # panid
            self.__panid = str(m)
        if(c is "f"):  # ownid
            self.__ownid = str(m)
        if(c is "u"):
            self.__pwr = int(m)
        if(c is "z"):
            self.__isStart = True
            self.__connect()
        return

    def __modeStart(self, data):
        print("[Simulator-Send] {0}".format(data))
        self.sock.send(data.encode())
        return

    def __connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(
                (self.__config.getHost(), int(self.__config.getPort()))
            )
            params = "{0:02X}{1:02X}{2:02X}{3:02X}{4}{5}".format(
                self.__bw, self.__sf, self.__ch, self._pwr, self.__panid, self.__ownid
            )
            self.sock.send(params.encode())
        except ConnectionRefusedError:  # 接続失敗
            print("[Error] 接続失敗")
        return
