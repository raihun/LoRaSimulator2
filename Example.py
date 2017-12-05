# -*- encoding:utf-8 -*-
from Network import Network
from Packet import Packet
from threading import Thread
from time import sleep


class Example:
    """ Loraクラスに対しての、Send/Recv基本形 """
    def __init__(self):
        self.network = Network()
        self.network.addRecvlistener(self.recvEvent)

        self.thSend = Thread(
            target=self.sendThread,
            args=(self.network,)
        )
        self.thSend.setDaemon(True)
        self.thSend.start()
        return

    def sendThread(self, network):
        while True:
            sleep(60.0)

            packet = Packet()
            packet.setDatalinkDst("0001")
            packet.setDatalinkSrc("0006")
            packet.setNetworkDst("0008")
            packet.setNetworkSrc("0006")
            packet.setPayload("__HELLO__")
            network.send(packet)
        return

    def recvEvent(self, msg):
        print("[Example-Recv] {0}".format(msg))
        return
