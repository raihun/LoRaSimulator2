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
    def send(self, data="", dstid="FFFF", ptype=0):
        # 送信パケット生成
        packet = Packet()
        panid = self.__config.getPanid()
        packet.setPanId(panid)
        datalinkDst = self.route.getNextnode(dstid)
        if(datalinkDst is None):
            datalinkDst = "FFFF"
        packet.setDatalinkDst(dstid)
        ownid = self.__config.getOwnid()
        packet.setDatalinkSrc(ownid)
        packet.setNetworkDst(dstid)
        packet.setNetworkSrc(ownid)
        packet.setPacketType(ptype)
        packet.setPayload(data)

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
        # super(Network, self).addRecvlistener(self.route.putRoute)
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

        # NW層自分宛て ではない場合
        # ownid = self.__config.getOwnid()
        # if(ownid is not packet.getNetworkDst()):
        #    return
        #  転送
        # super(Network, self).send(packet.exportPacket())

        """
            パケット結合部
        """
        # packetBuffer追加
        bufferId = "{0}{1}".format( packet.getNetworkDst(), packet.getNetworkSrc() )
        seq = packet.getSequenceNo()
        packetType = packet.getPacketType()

        findBuffer = False
        for i in range(len(self.__packetBuffer)):
            if(bufferId == self.__packetBuffer[i][0]):
                # シーケンス番号チェック
                if(self.__packetBuffer[i][1] >= seq):
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
        if(packetType != 2 and packetType != 6):
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
        self.route.putRoute(newMsg)

        # メッセージ転送
        global gRecvListeners
        for recvEvent in gRecvListeners:
            recvEvent(newMsg)
        return

    """ ルートリクエスト(10秒間隔) """
    @staticmethod
    def __broadcastThread(self, sendMethod, routeInst, ownid):
        while True:
            r = randrange(100, 200) / 10.0
            sleep(r)

            payload = "{0}00".format(ownid)
            payload += routeInst.getRoute(True)
            sendMethod(payload, "FFFF", 4)
        return
