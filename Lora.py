# -*- encoding:utf-8 -*-
from collections import deque
from Config import Config  # Config.py
from LoraFilter import LoraFilter  # LoraFilter.py
from threading import Thread
from time import sleep, time


class Lora:
    """ ES920LRを直接操作するクラス """

    def __init__(self):
        self.__config = Config()
        self.__connect()  # ES920LR Connect
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

    """ 初回インスタンス化時のみ有効となる接続/設定処理 """
    def __connect(self):
        # 初回起動チェック
        try:
            if(Lora.__isConnect):
                return
        except AttributeError:
            Lora.__isConnect = True
            Lora.__isStart = False
            Lora.__isLock = False

        # Check simulator mode
        mode = self.__config.getSimulator().strip().lower()
        if(mode in "true"):
            from Simulator import Serial
        else:
            from serial import Serial

        # Connect device
        devicename = self.__config.getDevicename()
        baudrate = self.__config.getBaudrate()
        try:
            Lora.device = Serial(devicename, int(baudrate))
        except Exception as e:
            print(e)
            return

        # ES920 Welcomeメッセージ待機
        sleep(3.0)

        # Set Send/Recv variables
        Lora.sendMessages = deque()
        Lora.recvListeners = []

        # 各種設定
        self.send(["2", "a 2"])
        self.send("b %s" % self.__config.getBandwidth())
        self.send("c %s" % self.__config.getSpreadingfactor())
        self.send("d %s" % self.__config.getChannel())
        self.send("e %s" % self.__config.getPanid())
        self.send("f %s" % self.__config.getOwnid())
        self.send(["l 2", "n 2", "o 1", "p 1", "q 1", "s 1"])
        self.send("u %s" % self.__config.getPower())
        self.send(["w", "z"])

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

    """ 送信待機スレッド """
    @staticmethod
    def __sendThread(self, device, sendMessages):
        while True:
            # 送信待機
            if(len(sendMessages) <= 0):
                sleep(0.01)
                continue

            # ロック時
            t = time()
            while(Lora.__isLock):
                if(time() - t > 10.0):  # タイムアウト
                    break
                sleep(0.01)

            # 送信待機メッセージキューからデキュー
            msg = sendMessages.popleft()
            if(msg is ""):
                continue

            # メッセージ送信
            cmd = msg.strip()
            cmd = "{0}\r\n".format(cmd).encode()
            device.write(cmd)

            # コマンド間隔
            if(Lora.__isStart):
                Lora.__isLock = True
            else:
                sleep(0.1)  # 設定時

            # スタート検知
            if(msg is "z"):
                Lora.__isStart = True
        return

    """ 受信待機スレッド """
    @staticmethod
    def __recvThread(self, device, recvListeners):
        lorafilter = LoraFilter()
        while True:
            # 受信待機
            if(device.inWaiting() <= 0):
                sleep(0.01)
                continue

            # UTF-8 に変換できない例外 (ES920LR電源投入時発生)
            try:
                line = device.readline().decode('utf-8').strip()
            except UnicodeDecodeError:
                continue

            # ロック解除
            if(line == "OK"):
                Lora.__isLock = False

            # フィルタリング
            line = lorafilter.recvFilter(line)
            if(line is None):
                continue

            # メッセージ転送
            for recvEvent in recvListeners:
                recvEvent(line)
        return
