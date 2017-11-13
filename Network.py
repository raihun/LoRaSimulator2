# -*- encoding:utf-8 -*-
from collections import deque
from Config import Config  # Config.py
from Lora import Lora  # Lora.py
from Packet import Packet  # Packet.py
from threading import Thread
from time import sleep, time


class Network:
    """
        ネットワークの基礎クラス
        ACK管理、TTL減算、
    """
    def __init__(self):
        # ownid 取得用
        self.__config = Config()

        # NIC生成
        self.__initNic()
        return

    """ 受信パケットを送るメソッドを追加 """
    def addRecvlistener(self, recvEvent):
        Network.recvListeners.append(recvEvent)
        return

    """
        初回インスタンス化時のみ有効となるNIC生成
        送信パケットキュー, 受信パケットキューを用意
    """
    def __initNic(self):
        # 初回起動チェック
        try:
            if(Network.__initNicMethod):
                return
        except AttributeError:
            Network.__initNicMethod = True

        # 各種変数/配列
        Network.ownid = self.__config.getOwnid()
        Network.sendPackets = deque()
        Network.recvListeners = []

        # 受信イベントメソッドを登録
        self.lora = Lora()
        self.lora.addRecvlistener(self.recvEvent)

        # 送信待機スレッド 作成
        self.__thSend = Thread(
            target=Network.__sendThread,
            args=(None, self.lora, Network.sendPackets)
        )
        self.__thSend.setDaemon(True)
        self.__thSend.start()

        # テストコード
        self.testThread = Thread(
            target=self.__sendThread2
        )
        self.testThread.setDaemon(True)
        self.testThread.start()
        return

    # テストメソッド
    def __sendThread2(self):
        sendPacket = Packet()
        sendPacket.setPanId("0001")
        sendPacket.setDatalinkDst("FFFF")
        sendPacket.setPacketType(0)
        p = ""
        for i in range(0, 0xFF):
            p = p + "."
        sendPacket.setPayload(p)
        Network.sendPackets.append(sendPacket)

    """ 送信待機スレッド """
    @staticmethod
    def __sendThread(self, lora, sendPackets):
        while True:
            # 送信待機
            if(len(sendPackets) <= 0):
                sleep(0.01)
                continue

            # 送信待機メッセージキューからデキュー
            sendPacket = sendPackets.popleft()

            # パケット送信
            lora.send(sendPacket.exportPacket())
        return

    """
        受信イベントメソッド
        LoraクラスがES920LRよりシリアル受信した際に呼び出される
    """
    def recvEvent(self, msg):
        # Ack packet
        ackPacket = Packet()
        ackPacket.importPacket(msg)
        if(ackPacket.getPacketType() is 0 or ackPacket.getPacketType() is 2):
            datalinkSrc = ackPacket.getDatalinkSrc()
            ackPacket.setDatalinkDst(datalinkSrc)
            ackPacket.setDatalinkSrc(Network.ownid)
            ackPacket.setNetworkDst(datalinkSrc)
            ackPacket.setNetworkSrc(Network.ownid)
            ackPacket.setPacketType(1)
            ackPacket.setTTL(31)
            ackPacket.setPayload("{0:02X}".format(ackPacket.getSequenceNo()))
            ackPacket.setSequenceNo(0)
            self.lora.send(ackPacket.exportPacket())

        # メッセージ転送
        for recvEvent in Network.recvListeners:
            recvPacket = Packet()
            recvPacket.setDatalinkDst(Network.ownid)
            recvPacket.importPacket(msg)
            recvEvent(recvPacket)
        return
