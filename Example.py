# -*- encoding:utf-8 -*-
import sys
from threading import Thread
import time
import Lora


class Example:
    def __init__(self):
        self.lora = Lora.Lora()
        self.lora.addRecvlistener(self.recvEvent)

        self.thSend = Thread(
            target=self.sendThread,
            args=(self.lora,)
        )
        self.thSend.setDaemon(True)
        self.thSend.start()
        return

    def sendThread(self, lora):
        while True:
            cmd = input()
            lora.send(cmd)
        return

    def recvEvent(self, msg):
        print(msg)
        return

Example = Example()

while True:
    time.sleep(0.01)
