# -*- encoding:utf-8 -*-
from Config import Config


class Packet:
    """
        このクラスでは、1パケットを定義する
        +--------+--------+--------+--------+--------+------+--------+--------+
        | PAN-ID | DL-Dst | NW-Dst | NW-Src | P-Type | TTL  | Seq-No | Payload|
        +--------+--------+--------+--------+--------+------+--------+--------+
        | 2Byte  | 2Byte  | 2Byte  | 2Byte  | 3bit   | 5bit | 1Byte  | var    |
        +--------+--------+--------+--------+--------+------+--------+--------+
    """
    def __init__(self):
        config = Config()
        self.setPanId(config.getPanid())
        return

    """ PAN-ID関連"""
    __panId = "0000"

    def setPanId(self, panid):
        self.__panId = panid
        return

    def getPanId(self):
        return self.__panId

    """ データリンク層関連 """
    __datalinkDst = "0000"

    def setDatalinkDst(self, nodeid):
        self.__datalinkDst = nodeid
        return

    def getDatalinkDst(self):
        return self.__datalinkDst

    __datalinkSrc = "0000"

    def setDatalinkSrc(self, nodeid):
        self.__datalinkSrc = nodeid
        return

    def getDatalinkSrc(self):
        return self.__datalinkSrc

    """ ネットワーク層関連 """
    __networkDst = "0000"

    def setNetworkDst(self, nodeid):
        self.__networkDst = nodeid
        return

    def getNetworkDst(self):
        return self.__networkDst

    __networkSrc = "0000"

    def setNetworkSrc(self, nodeid):
        self.__networkSrc = nodeid
        return

    def getNetworkSrc(self):
        return self.__networkSrc

    """
        パケットタイプ (3bit: 0-7)
        0(000): Normal
        1(001): Normal + ACK
        2(010): Normal + FIN
        3(011): Other (Payload 1Byte目がTypeとなる)
        4(100): Route
        5(101): Route + ACK
        6(110): Route + FIN
        7(111): Reserved
    """
    __packetType = 0

    def setPacketType(self, ptype):
        self.__packetType = ptype
        return

    def getPacketType(self):
        return self.__packetType

    """ TTL (5bit: 0-31) """
    __ttl = 31

    def setTTL(self, ttl):
        self.__ttl = ttl
        return

    def getTTL(self):
        return self.__ttl

    def decrementTTL(self):
        self.__ttl -= 1
        if self.__ttl <= 0:
            return False  # 失敗
        return True  # 成功

    """ シーケンス番号 (1Byte: 0-255) """
    __sequenceNo = 0

    def setSequenceNo(self, seq):
        self.__sequenceNo = seq
        return

    def getSequenceNo(self):
        return self.__sequenceNo

    """ ペイロード (可変) """
    __payload = ""

    def setPayload(self, payload):
        self.__payload = payload
        return

    def getPayload(self):
        return self.__payload

    """ RSSI値取得 """
    __rssi = -200

    def setRSSI(self, rssi):
        self.__rssi = rssi
        return

    def getRSSI(self):
        return self.__rssi

    """
        ------------------------------
        Packet クラス管理メソッド群
        ------------------------------
    """

    """ 生パケット -> Packet() """
    def importPacket(self, data):
        if len(data) < 24:  # フレーム長 未満
            return
        self.setRSSI(self.__convertRSSI(data[0:4]))
        self.setPanId(data[4:8])
        self.setDatalinkSrc(data[8:12])
        self.setNetworkDst(data[12:16])
        self.setNetworkSrc(data[16:20])
        margedData = int(data[20:22], 16)
        ptype, ttl = self.__purgeByte(margedData)
        self.setPacketType(ptype)
        self.setTTL(ttl)
        sequenceNo = int(data[22:24], 16)
        self.setSequenceNo(sequenceNo)

        if len(data) <= 24:  # ペイロードなし
            return
        self.setPayload(data[24:])
        return

    """ Packet() -> 生パケット (payload 38byte超えは複数パケ化) """
    def exportPacket(self):
        rawList = []
        splitPayload = self.__split_str(self.getPayload(), 38)
        size = len(splitPayload) - 1
        i = 0
        while True:
            raw = "{0}{1}{2}{3}".format(
                self.getPanId(),
                self.getDatalinkDst(),
                self.getNetworkDst(),
                self.getNetworkSrc()
            )
            if i >= size and self.getPacketType() == 0:
                self.setPacketType(2)
            if i >= size and self.getPacketType() == 4:
                self.setPacketType(6)
            raw += "{0:02X}".format(self.__mergeByte())
            raw += "{0:02X}".format(i % 0xFF)
            if size >= 0:
                raw += splitPayload[i]
            rawList.append(raw)
            i += 1
            if i > size:
                break
        return rawList

    """ Packet() -> 生パケット (1パケット転送用) """
    def transferPacket(self):
        raw = "{0}{1}{2}{3}".format(
            self.getPanId(),
            self.getDatalinkDst(),
            self.getNetworkDst(),
            self.getNetworkSrc()
        )
        raw += "{0:02X}".format(self.__mergeByte())
        raw += "{0:02X}".format(self.getSequenceNo())
        raw += self.getPayload()
        return raw

    """ 文字列を指定バイト数ごとに分割 """
    def __split_str(self, s, n):
        l = len(s)
        return [s[i:i+n] for i in range(0, l, n)]

    """ RSSI値 算出 """
    def __convertRSSI(self, rawrssi):
        rawrssi = int(rawrssi, 16)
        return -(rawrssi & 0x8000) | (rawrssi & 0x7FFF)

    """ Type + TTL 関連 """
    def __mergeByte(self):
        ptype = self.getPacketType()
        ttl = self.getTTL()
        return ptype << 5 | ttl

    def __purgeByte(self, data):
        return [data >> 5, data & 0x1F]
