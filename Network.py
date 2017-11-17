# -*- encoding:utf-8 -*-
from Config import Config
from Lora import Lora
from Packet import Packet
from Route import Route

class Network(Lora):
    """
        ネットワークの基礎クラス
        ACK、TTL、Repeater
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
        super(Network, self).send(data)
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

        # route
        route = Route()
        self.addRecvlistener(route.putRoute)

        # LoraのReceive Listenersに追加
        super(Network, self).addRecvlistener(self.recvEvent)
        return

    def recvEvent(self, msg):
        # 受信パケット
        packet = Packet()
        packet.importPacket(msg)

        # 自分宛てではない場合
        ownid = self.__config.getOwnid()

        #  転送
        # super(Network, self).send(packet.exportPacket())

        # メッセージ転送
        global gRecvListeners
        for recvEvent in gRecvListeners:
            recvEvent(msg)
        return
