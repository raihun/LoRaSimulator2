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

        # Get debug mode
        simulatorDebug = self.__config.getSimulatorDebug().strip().lower()
        if(simulatorDebug in "true"):
            self.__debug = True
        else:
            self.__debug = False
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
            self.recvmsg = self.sock.recv(128).decode().strip()
        except AttributeError:  # 接続よりも先に呼び出した場合
            return 0
        except ConnectionResetError:  # サーバ側からの切断
            self.sock.close()
        except OSError:  # サーバダウン
            print("[Simulator] 切断")
            self.sock.close()
            sys.exit()

        if(len(self.recvmsg) <= 0):
            self.sock.close()
        return len(self.recvmsg)

    def readline(self):
        msg = self.recvmsg.encode()
        if(self.__debug):
            print("[Simulator-Recv] {0}".format(msg))
        return msg

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
        if(self.__debug):
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
                self.__bw, self.__sf, self.__ch, self.__pwr, self.__panid, self.__ownid
            )
            self.sock.send(params.encode())
            print("[Simulator] 接続完了")
        except ConnectionRefusedError:  # 接続失敗
            print("[Simulator] 接続失敗")
        return
