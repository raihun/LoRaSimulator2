# -*- encoding:utf-8 -*-
from Config import Config
from Lora import Lora
from Packet import Packet
from random import randrange
from Route import Route
from threading import Thread
from time import sleep


class Network(Lora):
    """
        ネットワークの基礎クラス
        ACK、TTL、Repeater、パケ結合
    """
    def __init__(self):
        super(Network, self).__init__()
        self.__config = Config()
        self.__setting()
        return

    """ @override """
    def addRecvlistener(self, recvEvent):
        global gRecvListeners
        gRecvListeners.append(recvEvent)
        return

    """ @override """
    def send(self, packet):
        # 送信
        super(Network, self).send(packet.exportPacket())
        return

    """ 初回インスタンス化時のみ有効となる設定処理 """
    def __setting(self):
        # 初回起動チェック
        try:
            if(Network.__isSetting):
                return
        except AttributeError:
            Network.__isSetting = True

        # Set Send/Recv variables
        global gRecvListeners
        gRecvListeners = []

        # Route
        self.route = Route()
        self.__packetBuffer = []

        # LoraのReceive Listenersに追加
        super(Network, self).addRecvlistener(self.recvEvent)

        # broadcast Thread
        self.__thBroadcast = Thread(
            target=self.__broadcastThread,
            args=(
                None,
                self.send,
                self.route,
                self.__config.getPanid(),
                self.__config.getOwnid()
            )
        )
        self.__thBroadcast.setDaemon(True)
        self.__thBroadcast.start()
        return

    """ Loraから来るメッセージの2次フィルタリング """
    def recvEvent(self, msg):
        # パケットサイズエラーチェック
        if(len(msg) > 62):
            print("!!! ERROR (Java OutputStream) !!!")
            return

        # 受信パケット
        packet = Packet()
        packet.importPacket(msg)
        packetType = packet.getPacketType()
        networkDst = packet.getNetworkDst()

        """
            パケット転送部
        """
        ownid = self.__config.getOwnid()
        # NW層自分宛てではない AND パケットタイプが通常(0-3)の場合
        if (networkDst != ownid and (packetType in range(4))):
            print("Repeat!!!")
            datalinkDst = self.route.getNextnode(networkDst)
            if(datalinkDst is None):
                return
            packet.setDatalinkDst(datalinkDst)
            packet.setDatalinkSrc(ownid)
            if(packet.decrementTTL()):  # TTL減算チェック
                super(Network, self).send(packet.exportPacket())
            return

        """
            パケット結合部
        """
        # packetBuffer追加
        bufferId = "{0}{1}".format(
            packet.getNetworkDst(),
            packet.getNetworkSrc()
        )
        seq = packet.getSequenceNo()

        findBuffer = False
        for i in range(len(self.__packetBuffer)):
            if(bufferId == self.__packetBuffer[i][0]):
                # シーケンス番号チェック
                if(self.__packetBuffer[i][1] >= seq):
                    self.__packetBuffer.pop(i)
                    return
                self.__packetBuffer[i][1] = seq
                self.__packetBuffer[i][2] = "{0}{1}".format(
                    self.__packetBuffer[i][2],
                    packet.getPayload()
                )
                findBuffer = True
                break
        if(not findBuffer and seq == 0):
            self.__packetBuffer.append([bufferId, seq, packet.getPayload()])

        # packetTypeチェック (FINの場合、メッセージ転送へ)
        if not (packetType in [2, 6]):
            return

        # パケット結合
        payloadBuffer = ""
        for i in range(len(self.__packetBuffer)):
            if(bufferId == self.__packetBuffer[i][0]):
                payloadBuffer = self.__packetBuffer[i][2]
                self.__packetBuffer.pop(i)
                break
        newMsg = msg[:24] + payloadBuffer

        """
            メッセージ転送
        """
        # Routeへ転送
        if(packetType == 6):
            self.route.putRoute(newMsg)

        # メッセージ転送
        global gRecvListeners
        for recvEvent in gRecvListeners:
            recvEvent(newMsg)
        return

    """ ルートリクエスト(10秒間隔) """
    @staticmethod
    def __broadcastThread(self, sendMethod, routeInst, panid, ownid):
        while True:
            # 待機
            r = randrange(100, 200) / 10.0
            sleep(r)

            # Payload生成
            payload = "{0}00".format(ownid)
            payload += routeInst.getRoute(True)

            # 送信パケット生成
            packet = Packet()
            packet.setPanId(panid)
            packet.setDatalinkDst("FFFF")
            packet.setDatalinkSrc(ownid)
            packet.setNetworkDst("FFFF")
            packet.setNetworkSrc(ownid)
            packet.setPacketType(4)
            packet.setPayload(payload)

            # 送信
            sendMethod(packet)
        return
