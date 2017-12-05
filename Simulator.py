# -*- encoding:utf-8 -*-
from Config import Config
import socket
import sys


class Simulator:
    """
        ES920LRシミュレータ サーバとのインタフェース
    """
    def __init__(self, devicename, baudrate):
        self.__config = Config()
        self.__isStart = False

        # Get debug mode
        debug = self.__config.getSimulatorDebug().strip().lower()
        if debug in "true":
            self.__debug = True
        else:
            self.__debug = False
        return

    def write(self, rawdata):
        data = rawdata.decode('utf-8').strip()
        if not self.__isStart:
            self.__modeConfig(data)
        else:
            self.__modeStart(data)
        return

    def inWaiting(self):
        if not self.__isStart:
            return 0
        try:
            self.__recvmsg = self.__sock.recv(1024).decode().strip()
        except AttributeError:  # 接続よりも先に呼び出した場合
            return 0
        except ConnectionResetError:  # サーバ側からの切断
            self.__sock.close()
        except OSError:  # サーバダウン
            print("[Simulator] 切断")
            self.__sock.close()
            sys.exit()

        if len(self.__recvmsg) <= 0:
            self.__sock.close()
        return len(self.__recvmsg)

    def readline(self):
        msg = self.__recvmsg.encode()
        if self.__debug:
            print("[Simulator-Recv] {0}".format(msg))
        return msg

    def __modeConfig(self, data):
        # Split command
        data = data.split(" ")
        c = data[0]
        if len(data) > 1:
            m = data[1]

        # Set parameters
        if c == "b":  # bw
            self.__bw = int(m)
        if c == "c":  # sf
            self.__sf = int(m)
        if c == "d":  # channel
            self.__ch = int(m)
        if c == "e":  # panid
            self.__panid = str(m)
        if c == "f":  # ownid
            self.__ownid = str(m)
        if c == "u":
            self.__pwr = int(m)
        if c == "z":
            self.__isStart = True
            self.__connect()
        return

    def __modeStart(self, data):
        if self.__debug:
            print("[Simulator-Send] {0}".format(data))
        self.__sock.send(data.encode())
        return

    def __connect(self):
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect(
                (self.__config.getHost(), int(self.__config.getPort()))
            )
            params = "{0:02X}{1:02X}{2:02X}{3:02X}{4}{5}".format(
                self.__bw, self.__sf, self.__ch, self.__pwr,
                self.__panid, self.__ownid
            )
            self.__sock.send(params.encode())
            print("[Simulator] 接続完了")
        except ConnectionRefusedError:  # 接続失敗
            print("[Simulator] 接続失敗")
        return
