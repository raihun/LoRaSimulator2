# -*- encoding:utf-8 -*-

import re
import time
from threading import Thread

from Packet import Packet

class Route:
    """
        このクラスでは、ルーティングテーブルを構築する
        ルーティングテーブルの格納順
        +- ----------+-------------+----------+------------+------+
        | networkDst | datalinkDst | hopCount | aliveCount | rssi |
        +------ -----+-------------+----------+------------+------+
    """
    __INDEX_NWDST = 0
    __INDEX_DLDST = 1
    __INDEX_HOP = 2
    __INDEX_ALIVE = 3
    __INDEX_RSSI = 4

    __ALIVE_TIME = 60
    __routeList = []

    def __init__(self):
        self.__packet = Packet()

        self.thCountAlive = Thread(target=self.__countDownAliveTime,)
        self.thCountAlive.setDaemon(True)
        self.thCountAlive.start()
        return


    def getNextnode(self, datalinkDst):
        """
            ネットワーク層の、宛先IDを引数に渡すと、
            次に転送するべきノードID(データリンク層宛先ID)を返す
            datalinkDst="000A"などの文字列4桁
        """
        nextDstList = self.select("des", datalinkDst)
        if not any(nextDstList):
            return None
        selectHopsList = [nextDst[self.__INDEX_HOP] for nextDst in nextDstList]

        return nextDstList[selectHopsList.index(min(selectHopsList))][1]


    def select(self, columnName="", data=""):
        """
            ルーティングテーブルからカラムとデータを指定で
            対象のリストを返す
            引数なしですべてのルーティングテーブルのリストを返す
        """
        if columnName == "":
            return self.__routeList
        elif re.compile(columnName, re.IGNORECASE).match("des") is not None:
            return list(filter(lambda x: x[0] == data, self.__routeList))
        elif re.compile(columnName, re.IGNORECASE).match("datalinkDst") is not None:
            return list(filter(lambda x: x[1] == data, self.__routeList))
        elif re.compile(columnName, re.IGNORECASE).match("hop") is not None:
            return list(filter(lambda x: x[2] == data, self.__routeList))
        elif re.compile(columnName, re.IGNORECASE).match("aliveCount") is not None:
            return list(filter(lambda x: x[3] == data, self.__routeList))
        elif re.compile(columnName, re.IGNORECASE).match("RSSI") is not None:
            return list(filter(lambda x: x[4] == data, self.__routeList))
        else:
            return


    def putRoute(self, msg):
        """
            TODO 重複ルートのチェック機構(ルーティングテーブルから削除するため)
            送られてきたルーティングテーブルを自分のテーブルに追加する
            通常パケットの場合はaliveCountを60に変更する
        """
        self.__packet.importPacket(msg)
        rssi = self.__packet.getRSSI()
        payload = self.__packet.getPayload()
        packetType = self.__packet.getPacketType()
        datalinkDst = self.__packet.getDatalinkSrc()

        if not (packetType == 4 or packetType == 5 or packetType == 6):
            self.__resetAliveTime(datalinkDst)
            return

        recvTables = [payload[i * 6:i * 6 + 6]
                      for i in range(int(len(payload) / 6))]

        for i in range(len(self.__routeList)):
            for table in recvTables:
                if (self.__routeList[i][self.__INDEX_NWDST] == table[:4] and
                        self.__routeList[i][self.__INDEX_DLDST] == datalinkDst):

                    self.__routeList[i] = [
                        table[:4],               # networkDst
                        datalinkDst,
                        int(table[4:6], 16) + 1, # hop + 1
                        self.__ALIVE_TIME,
                        rssi
                    ]

                    del(recvTables[recvTables.index(table)])

        self.__routeList.extend([[table[0:4], datalinkDst, 1 + int(
            table[4:6], 16), self.__ALIVE_TIME, rssi] for table in recvTables])
        print(self.__routeList)
        return


    def __resetAliveTime(self, datalinkDst):
        """ 通常パケットが届いたときに，aliveTimeを更新する """
        for i in range(len(self.__routeList)):
            if self.__routeList[i][self.__INDEX_DLDST] == datalinkDst:
                self.__routeList[i][self.__INDEX_ALIVE] = self.__ALIVE_TIME
        return


    def __countDownAliveTime(self):
        """
            aliveCountをカウントダウンする
            60から0までデクリメントし，0になるとそのルーティングのホップ数を最大の255にセットする
        """
        while True:
            time.sleep(1)
            for i in range(len(self.__routeList)):
                if self.__routeList[i][self.__INDEX_ALIVE] <= 0:
                    self.__routeList[i][self.__INDEX_HOP] = 255
                    continue
                self.__routeList[i][self.__INDEX_ALIVE] = self.__routeList[i][self.__INDEX_ALIVE] - 1
