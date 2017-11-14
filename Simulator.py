# -*- encoding:utf-8 -*-


class Simulator:
    """
        このクラスでは、ES920LRのシミュレータを作成する
    """
    def __init__(self, devicename, baudrate):
        self.flg = 0
        return

    def write(self, data):
        print("[Sim in] {0}".format(data))
        self.flg = 1
        return

    def inWaiting(self):
        return self.flg

    def readline(self):
        self.flg = 0
        return "OK".encode()
