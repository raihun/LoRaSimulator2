# -*- encoding:utf-8 -*-

from Config import Config
from Packet import Packet
import re
from time import sleep
from threading import Thread


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

    __ALIVE_TIME = 120
    __routeList = []

    def __init__(self):
        self.__config = Config()
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

        # 最小HOP数がMAXになってしまった場合
        if min(selectHopsList) >= 255:
            return None

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

        if not (packetType in [4, 5, 6]):
            self.__resetAliveTime(datalinkDst)
            return

        _recvTables = [payload[i * 6:i * 6 + 6]
                      for i in range(int(len(payload) / 6))]

        # ネットワーク層宛先IDが自分宛ての場合、不要な情報のため除外する
        recvTables = []
        for i in range(len(_recvTables)):
            if _recvTables[i][:4] != self.__config.getOwnid():
                recvTables.append(_recvTables[i])

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
        """
        print("------------------------------")
        for data in self.getRoute(False):
            print("{0} {1} {2} {3}".format(data[0], self.getNextnode(data[0]), data[1], data[2]))
        """
        return

    def getRoute(self, resultType=False):
        # ネットワーク層宛先, 最短Hopのリスト作成
        resultTables = []
        for i in range(len(self.__routeList)):
            # routeListより必要パラメータ取得
            nwDst = self.__routeList[i][self.__INDEX_NWDST]
            hop = self.__routeList[i][self.__INDEX_HOP]
            rssi = self.__routeList[i][self.__INDEX_RSSI]

            # 重複確認を行いつつ、最適のresultTablesを作成
            findFlag = False
            for j in range(len(resultTables)):
                # HOP数が同じ場合、RSSI値によって判断
                if resultTables[j][0] == nwDst and resultTables[j][1] == hop:
                    if resultTables[j][2] < rssi:
                        resultTables[j][1] = hop
                        resultTables[j][2] = rssi
                    findFlag = True
                # HOP数が少ない場合、上書き
                elif resultTables[j][0] == nwDst and resultTables[j][1] > hop:
                    resultTables[j][1] = hop
                    findFlag = True
                # HOP数が多い場合でも、フラグを立ててresultTablesへの追加を防ぐ
                elif resultTables[j][0] == nwDst:
                    findFlag = True
            if not findFlag:
                resultTables.append([nwDst, hop, rssi])

        if not resultType:
            return resultTables

        # payload部作成
        payload = ""
        for i in range(len(resultTables)):
            payload += "{0}{1:02X}".format(
                resultTables[i][0],
                resultTables[i][1]
            )
        return payload

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
            sleep(1)
            for i in range(len(self.__routeList)):
                if self.__routeList[i][self.__INDEX_ALIVE] <= 0:
                    self.__routeList[i][self.__INDEX_HOP] = 255
                    continue
                self.__routeList[i][self.__INDEX_ALIVE] = self.__routeList[i][self.__INDEX_ALIVE] - 1
