# -*- encoding:utf-8 -*-
from collections import deque
from Config import Config
from Lora import Lora
from Packet import Packet
from random import randrange
from Route import Route
from threading import Thread
from time import sleep, time


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

    """ 初回インスタンス化時のみ有効となる設定処理 """
    def __setting(self):
        # 初回起動チェック
        try:
            if Network.__isSetting:
                return
        except AttributeError:
            Network.__isSetting = True

        # Set Send/Recv variables
        global gRecvListeners
        gRecvListeners = []

        # Route
        self.route = Route()

        # other
        Network.__sendPacketBuffer = deque()
        self.__recvPacketBuffer = []

        # LoraのReceive Listenersに追加
        super(Network, self).addRecvlistener(self.recvEvent)

        # Send thread
        self.__thSend = Thread(
            target=self.__sendThread,
            args=(
                None,
                super(Network, self).send,
                Network.__sendPacketBuffer
            )
        )
        self.__thSend.setDaemon(True)
        self.__thSend.start()

        # Broadcast Thread
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

    """ @override """
    def addRecvlistener(self, recvEvent):
        global gRecvListeners
        gRecvListeners.append(recvEvent)
        return

    """ @override """
    def send(self, packet, transfer=False):
        # ACKパケット送信時
        if packet.getPacketType() == 1:
            super(Network, self).send(packet.transferPacket())
            return

        # ルーティング系パケット 送信時
        if packet.getPacketType() in [4, 5, 6]:
            super(Network, self).send(packet.exportPacket())
            return

        # 通常パケット
        if not transfer:
            for raw in packet.exportPacket():
                bufferId = "{0}{1}{2}".format(
                    packet.getNetworkDst(),
                    packet.getNetworkSrc(),
                    raw[18:20]
                )
                Network.__sendPacketBuffer.append([bufferId, raw, True])
            return

        bufferId = "{0}{1}{2:02X}".format(
            packet.getNetworkDst(),
            packet.getNetworkSrc(),
            packet.getSequenceNo()
        )
        Network.__sendPacketBuffer.append([bufferId, packet, False])
        return

    """ Loraから来るメッセージの2次フィルタリング """
    def recvEvent(self, msg):
        # パケットサイズエラーチェック
        if len(msg) > 62:
            print("!!! ERROR (Java OutputStream) !!!")
            return

        # 受信パケット
        ownid = self.__config.getOwnid()
        packet = Packet()
        packet.importPacket(msg)
        packetType = packet.getPacketType()
        datalinkSrc = packet.getDatalinkSrc()
        networkDst = packet.getNetworkDst()

        """
            ACKパケット
        """
        # 生成・送信
        if packetType in [0, 2]:
            ackPacket = Packet()
            ackPacket.importPacket(msg)
            ackPacket.setPanId(self.__config.getPanid())
            ackPacket.setDatalinkDst(datalinkSrc)
            ackPacket.setDatalinkSrc(ownid)
            ackPacket.setPacketType(1)
            self.send(ackPacket, True)

        # 受信
        if packetType == 1:
            bufferId = "{0}{1}{2:02X}".format(
                packet.getNetworkDst(),
                packet.getNetworkSrc(),
                packet.getSequenceNo()
            )
            if len(Network.__sendPacketBuffer) <= 0:
                return
            if Network.__sendPacketBuffer[0][0] == bufferId:
                Network.__sendPacketBuffer.popleft()
            return

        """
            パケット転送部
        """
        # NW層自分宛てではない AND パケットタイプが通常(0, 2)の場合
        if networkDst != ownid and (packetType in [0, 2]):
            datalinkDst = self.route.getNextnode(networkDst)
            if datalinkDst == None:
                return
            packet.setDatalinkDst(datalinkDst)
            packet.setDatalinkSrc(ownid)
            if packet.decrementTTL():  # TTL減算チェック
                self.send(packet, True)
            return

        """
            パケット結合部
        """
        # recvPacketBuffer追加
        bufferId = "{0}{1}".format(
            packet.getNetworkDst(),
            packet.getNetworkSrc()
        )
        seq = packet.getSequenceNo()

        findBuffer = False
        for i in range(len(self.__recvPacketBuffer)):
            if bufferId == self.__recvPacketBuffer[i][0]:
                # シーケンス番号チェック
                if self.__recvPacketBuffer[i][1] >= seq:
                    self.__recvPacketBuffer.pop(i)
                    return
                self.__recvPacketBuffer[i][1] = seq
                self.__recvPacketBuffer[i][2] += packet.getPayload()
                findBuffer = True
                break
        if not findBuffer and seq == 0:
            self.__recvPacketBuffer.append(
                [bufferId, seq, packet.getPayload()]
            )

        # packetTypeチェック (FINの場合、メッセージ転送へ)
        if not (packetType in [2, 6]):
            return

        # パケット結合
        payloadBuffer = ""
        for i in range(len(self.__recvPacketBuffer)):
            if bufferId == self.__recvPacketBuffer[i][0]:
                payloadBuffer = self.__recvPacketBuffer[i][2]
                self.__recvPacketBuffer.pop(i)
                break
        if payloadBuffer == "":
            return
        newMsg = msg[:24] + payloadBuffer

        """
            メッセージ転送
        """
        print("Receive: ", newMsg)

        # Routeへ転送
        if packetType == 6:
            self.route.putRoute(newMsg)

        # メッセージ転送
        global gRecvListeners
        for recvEvent in gRecvListeners:
            recvEvent(newMsg)
        return

    """ 送信待機スレッド """
    @staticmethod
    def __sendThread(self, superSendMethod, sendPacketBuffer):
        t = time()
        while True:
            # カウントダウン
            if time() - t >= 1.0:
                t = time()
            else:
                sleep(0.01)
                continue

            # 送信待機
            if len(sendPacketBuffer) <= 0:
                sleep(0.01)
                continue

            # 送信
            if sendPacketBuffer[0][2]:
                superSendMethod(sendPacketBuffer[0][1])
            else:
                superSendMethod(sendPacketBuffer[0][1].transferPacket())
        return

    """ ルートリクエスト(10秒間隔) """
    @staticmethod
    def __broadcastThread(self, sendMethod, routeInst, panid, ownid):
        while True:
            # 待機
            r = randrange(200, 300) / 10.0
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
