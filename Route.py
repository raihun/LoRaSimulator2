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
    __routeTable = []

    def __init__(self):
        self.__config = Config()
        self.thCountAlive = Thread(target=self.__countDownAliveTime,)
        self.thCountAlive.setDaemon(True)
        self.thCountAlive.start()
        return

    def getNextnode(self, networkDst):
        """
            ネットワーク層の、宛先IDを引数に渡すと、
            次に転送するべきノードID(データリンク層宛先ID)を返す
        """

        # ルーティングテーブルより、ネットワーク層宛先IDで検索
        matchList = self.search("nwdst", networkDst)
        if not any(matchList):
            return None

        # ホップ数リスト生成
        hopList = [m['HOP'] for m in matchList]
        if min(hopList) >= 255:  # 最小HOP数がMAX(=時間切れ)の場合
            return None

        # RSSI値で最適DLDSTを探索
        minHopList = []
        for m in matchList:
            if m['HOP'] == min(hopList):
                minHopList.append(m)
        sortedList = sorted(minHopList, key=lambda x:-x['RSSI'])

        return sortedList[0]['DLDST']

    def search(self, columnName="", data=""):
        """
            ルーティングテーブルからカラムとデータを指定で
            対象のリストを返す
            引数なしですべてのルーティングテーブルのリストを返す
        """
        if columnName == "":
            return self.__routeTable
        elif re.compile(columnName, re.IGNORECASE).match("nwdst") is not None:
            return list(filter(lambda x: x['NWDST'] == data, self.__routeTable))
        elif re.compile(columnName, re.IGNORECASE).match("dldst") is not None:
            return list(filter(lambda x: x['DLDST'] == data, self.__routeTable))
        elif re.compile(columnName, re.IGNORECASE).match("hop") is not None:
            return list(filter(lambda x: x['HOP'] == data, self.__routeTable))
        elif re.compile(columnName, re.IGNORECASE).match("time") is not None:
            return list(filter(lambda x: x['TIME'] == data, self.__routeTable))
        elif re.compile(columnName, re.IGNORECASE).match("rssi") is not None:
            return list(filter(lambda x: x['RSSI'] == data, self.__routeTable))
        else:
            return

    def putRoute(self, msg):
        """
            送られてきたルーティングテーブルを自分のテーブルに追加する
        """
        packet = Packet()
        packet.importPacket(msg)
        rssi = packet.getRSSI()
        dlsrc = packet.getDatalinkSrc()
        payload = packet.getPayload()

        self.__resetAliveTime(dlsrc, rssi)

        payloadLength = int(len(payload) / 6)
        payloadList = [payload[i * 6:i * 6 + 6] for i in range(payloadLength)]

        for p in payloadList:
            nwdst = p[:4]
            hop = int(p[4:6], 16)

            # ネットワーク層宛先IDが自分宛ての場合、不要な情報のため除外する
            if nwdst == self.__config.getOwnid():
                continue

            # 重複データのため、除外する
            find = False
            for t in self.__routeTable:
                if t['NWDST'] == nwdst and t['DLDST'] == dlsrc:
                    find = True
            if find:
                continue

            # 追加
            self.__routeTable.append({
                'NWDST': nwdst,
                'DLDST': dlsrc,
                'HOP':   hop + 1,
                'TIME':  self.__ALIVE_TIME,
                'RSSI':  rssi
            })
        return

    def getRoute(self):
        result = []  # NW層宛先, 最短Hopのリスト
        for t in self.__routeTable:
            find = False  # 重複確認を行いつつ、最適のresultを作成
            for r in result:
                if r['NWDST'] != t['NWDST']:  # 重複していない場合
                    continue
                find = True  # 重複フラグ
                if r['HOP'] > t['HOP']:  # HOP数が少ない場合、上書き
                    r['HOP'] = t['HOP']
            if not find:
                result.append({'NWDST':t['NWDST'], 'HOP':t['HOP']})

        # payload部作成
        payload = ""
        for r in result:
            payload += "{0}{1:02X}".format(r['NWDST'], r['HOP'])
        return payload

    def __resetAliveTime(self, datalinkSrc, rssi):
        """ aliveTimeを更新する """
        for r in self.__routeTable:
            if r['DLDST'] == datalinkSrc:
                r['TIME'] = self.__ALIVE_TIME
                r['RSSI'] = rssi
        return

    def __countDownAliveTime(self):
        """ aliveCountをカウントダウンする """
        while True:
            sleep(1)
            for r in self.__routeTable:
                r['TIME'] -= 1
                if r['TIME'] <= 0:
                    r['HOP'] = 255
                    continue
