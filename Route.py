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
        +------------+-------------+----------+------------+------+
        | networkDst | datalinkDst | hopCount | aliveCount | rssi |
        +------------+-------------+----------+------------+------+
    """

    __ALIVE_TIME = 120
    __routeList = []

    def __init__(self):
        self.__config = Config()
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
        selectHopsList = [nextDst['HOP'] for nextDst in nextDstList]

        if min(selectHopsList) >= 255:  # 最小HOP数がMAXの場合
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
            送られてきたルーティングテーブルを自分のテーブルに追加する
        """
        packet = Packet()
        packet.importPacket(msg)
        payload = packet.getPayload()
        datalinkSrc = packet.getDatalinkSrc()

        self.__resetAliveTime(datalinkSrc)

        recvTables = [payload[i * 6:i * 6 + 6]
                      for i in range(int(len(payload) / 6))]

        for rt in recvTables:
            nwdst = rt[:4]
            hop = int(rt[4:6], 16)

            # ネットワーク層宛先IDが自分宛ての場合、不要な情報のため除外する
            if nwdst == self.__config.getOwnid():
                continue

            # 重複データのため、除外する
            findFlag = False
            for rl in self.__routeList:
                if rl['NWDST'] == nwdst and rl['DLDST'] == datalinkSrc:
                    findFlag = True
            if findFlag:
                continue

            # 追加
            self.__routeList.append({
                'NWDST': nwdst,
                'DLDST': datalinkSrc,
                'HOP':   hop + 1,
                'TIME':  self.__ALIVE_TIME,
                'RSSI':  packet.getRSSI()
            })
        return

    def getRoute(self):
        resultTables = []  # ネットワーク層宛先, 最短Hopのリスト
        for rl in self.__routeList:
            findFlag = False  # 重複確認を行いつつ、最適のresultTablesを作成
            for rt in resultTables:
                if rt['NWDST'] == rl['NWDST']:
                    findFlag = True
                    # HOP数が同じ場合、RSSI値によって判断
                    if rt['HOP'] == rl['HOP']:
                        if rt['RSSI'] < rl['RSSI']:
                            rt['HOP'] = rl['HOP']
                            rt['RSSI'] = rl['RSSI']
                    # HOP数が少ない場合、上書き
                    elif rt['HOP'] > rl['HOP']:
                        rt['HOP'] = rl['HOP']
            if not findFlag:
                resultTables.append({
                    'NWDST': rl['NWDST'],
                    'HOP': rl['HOP'],
                    'RSSI': rl['RSSI']
                })

        # payload部作成
        payload = ""
        for r in resultTables:
            payload += "{0}{1:02X}".format(r['NWDST'], r['HOP'])
        return payload

    def __resetAliveTime(self, datalinkSrc):
        """ aliveTimeを更新する """
        for r in self.__routeList:
            if r['DLDST'] == datalinkSrc:
                r['TIME'] = self.__ALIVE_TIME
        return

    def __countDownAliveTime(self):
        """
            aliveCountをカウントダウンする
            60から0までデクリメントし、0になるとそのルーティングのホップ数を
            最大の255にセットする
        """
        while True:
            sleep(1)
            for r in self.__routeList:
                r['TIME'] -= 1
                if r['TIME'] <= 0:
                    r['HOP'] = 255
                    continue
