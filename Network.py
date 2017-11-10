# -*- encoding:utf-8 -*-
from Lora import Lora
from Packet import Packet
from threading import Thread


class Network:
    """
        ネットワークの基礎クラス
        ACK管理、TTL減算、
    """
    def __init__(self):
        self.lora = Lora()
        self.lora.addRecvlistener(self.recvEvent)

        self.packet = Packet()
        return

    def recvEvent(self, msg):
        self.packet.importPacket(msg)
        return
