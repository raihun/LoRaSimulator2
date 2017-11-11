# -*- encoding:utf-8 -*-
from Lora import Lora
from Packet import Packet
from threading import Thread
from time import sleep


class Network:
    """
        ネットワークの基礎クラス
        ACK管理、TTL減算、
    """
    def __init__(self):
        self.lora = Lora()
        self.lora.addRecvlistener(self.recvEvent)
        self.recvPacket = Packet()

        self.thSend = Thread(
            target=self.sendThread,
            args=(self.lora,)
        )
        self.thSend.setDaemon(True)
        self.thSend.start()
        return

    def sendThread(self, lora):
        while True:
            p = Packet()
            p.setPanId("0001")
            p.setDatalinkDst("0002")
            p.setDatalinkSrc("0001")
            p.setNetworkDst("0002")
            p.setNetworkSrc("0001")
            p.setPacketType(7)
            p.setTTL(31)
            p.setSequenceNo(255)
            p.setPayload("HELLO")

            lora.send(p.exportPacket())
            sleep(5.0)
        return

    def recvEvent(self, msg):
        self.recvPacket.importPacket(msg)
        return
