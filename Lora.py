# -*- encoding:utf-8 -*-
from collections import deque
from Config import Config  # Config.py
from serial import Serial
from threading import Thread
from time import sleep


class Lora:
    """ ES920LRを直接操作するクラス """
    def __init__(self):
        self.__config = Config()
        self.__connect()  # ES920LR Connect
        self.__setting()  # ES920LR Setting
        return

    """ シリアル通信の受信メッセージを送るメソッドを追加 """
    def addRecvlistener(self, recvEvent):
        Lora.recvListeners.append(recvEvent)
        return

    """
        シリアル通信の送信メッセージを送るメソッド
        文字列, 文字列配列 両方対応
    """
    def send(self, data):
        if(type(data) == list):
            for datum in data:
                Lora.sendMessages.append(datum)
        else:
            Lora.sendMessages.append(data)
        return

    """ 初回インスタンス化時のみ有効となる接続処理 """
    def __connect(self):
        # 初回起動チェック
        try:
            if(Lora.isConnect):
                return
        except AttributeError:
            Lora.isConnect = True

        # Connect device
        devicename = self.__config.getDevicename()
        baudrate = self.__config.getBaudrate()
        try:
            Lora.device = Serial(devicename, int(baudrate))
        except Exception as e:
            print(e)
            return

        # Set Send/Recv variables
        Lora.sendMessages = deque()
        Lora.recvListeners = []

        # Send thread
        self.__thSend = Thread(
            target=self.__sendThread,
            args=(None, Lora.device, Lora.sendMessages)
        )
        self.__thSend.setDaemon(True)
        self.__thSend.start()

        # Receive thread
        self.__thRecv = Thread(
            target=self.__recvThread,
            args=(None, Lora.device, Lora.recvListeners)
        )
        self.__thRecv.setDaemon(True)
        self.__thRecv.start()
        return

    """ 初回インスタンス化時のみ有効となる設定処理 """
    def __setting(self):
        # 初回起動チェック
        try:
            if(Lora.initSetting):
                return
        except AttributeError:
            Lora.initSetting = True

        # 各種設定
        sleep(3.0)
        self.send(["2", "a 2"])
        self.send("b %s" % self.__config.getBandwidth())
        self.send("c %s" % self.__config.getSpreadingfactor())
        self.send("d %s" % self.__config.getChannel())
        self.send("e %s" % self.__config.getPanid())
        self.send("f %s" % self.__config.getOwnid())
        self.send(["l 2", "n 2", "o 1", "p 1", "q 1", "s 1"])
        self.send("u %s" % self.__config.getPower())
        self.send(["w", "z"])
        return

    """ 送信待機スレッド """
    @staticmethod
    def __sendThread(self, device, sendMessages):
        while True:
            if(len(sendMessages) <= 0):  # 送信待機
                sleep(0.01)
                continue
            msg = sendMessages.popleft()
            if(msg == ""):
                continue
            cmd = msg.strip()
            cmd = "{0}\r\n".format(cmd).encode()
            device.write(cmd)
            sleep(0.1)  # コマンド間隔 最低100ms必要
        return

    """ 受信待機スレッド """
    @staticmethod
    def __recvThread(self, device, recvListeners):
        while True:
            if(device.inWaiting() <= 0):  # 受信待機
                sleep(0.01)
                continue
            try:
                line = device.readline().decode('utf-8').strip()
            except UnicodeDecodeError:
                continue
            if(line != ""):
                for recvEvent in recvListeners:
                    recvEvent(line)
        return
