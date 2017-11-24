# -*- encoding:utf-8 -*-
from Config import Config
from Lora import Lora
from Packet import Packet
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
        super(Network, self).addRecvlistener(self.route.putRoute)

        # LoraのReceive Listenersに追加
        super(Network, self).addRecvlistener(self.recvEvent)

        # broadcast Thread
        self.__thBroadcast = Thread(
            target=self.__broadcastThread,
            args=(None, self.send)
        )
        self.__thBroadcast.setDaemon(True)
        self.__thBroadcast.start()
        return

    """ Loraのから来るメッセージの2次フィルタリング """
    def recvEvent(self, msg):
        # 受信パケット
        packet = Packet()
        packet.importPacket(msg)

        # NW層自分宛て ではない場合
        ownid = self.__config.getOwnid()
        if(ownid is not packet.getNetworkDst()):
            return

        #  転送
        # super(Network, self).send(packet.exportPacket())

        # メッセージ転送
        global gRecvListeners
        for recvEvent in gRecvListeners:
            recvEvent(msg)
        return

    """ ルートリクエスト(10秒間隔) """
    @staticmethod
    def __broadcastThread(self, sendMethod):
        while True:
            sendMethod("0001FFFFOK", "FFFF", 4)
            sleep(10)
        return
