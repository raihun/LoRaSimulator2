# -*- encoding:utf-8 -*-
from Network import Network
from threading import Thread


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
            cmd = input()
            network.send(cmd)
        return

    def recvEvent(self, msg):
        print("[Example-Recv] {0}".format(msg))
        return
