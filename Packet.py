# -*- encoding:utf-8 -*-


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
        0: 通常パケット
        1: 通常パケット(終了)
        2: ACK
        3: ルートブロードキャスト
        4: Reserved
        5: Reserved
        6: Reserved
        7: Reserved
    """
    __packetType = 0

    def setPacketType(self, ptype):
        self.__packetType = ptype
        return

    def getPacketType(self):
        return self.__packetType

    """ TTL (5bit: 0-31) """
    __ttl = 0

    def setTTL(self, ttl):
        self.__ttl = ttl
        return

    def getTTL(self):
        return self.__ttl

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
        print(data)
        # フレーム長 未満
        if(len(data) < 24):
            return
        self.setRSSI(self.convertRSSI(data[0:4]))
        self.setPanId(data[4:8])
        self.setDatalinkSrc(data[8:12])
        self.setNetworkDst(data[12:16])
        self.setNetworkDst(data[16:20])
        margedData = int(data[20:22], 16)
        ptype, ttl = self.purgeByte(margedData)
        self.setPacketType(ptype)
        self.setTTL(ttl)
        sequenceNo = int(data[22:24], 16)
        self.setSequenceNo(sequenceNo)

        # ペイロードなし
        if(len(data) <= 24):
            return

        self.setPayload(data[24:])
        return

    """ Packet() -> 生パケット """
    def exportPacket(self):

        return

    """ RSSI値 算出 """
    def convertRSSI(self, rawrssi):
        rawrssi = int(rawrssi, 16)
        return -(rawrssi & 0x8000) | (rawrssi & 0x7FFF)

    """ Type + TTL 関連 """
    def mergeByte(self):
        ptype = self.getPacketType()
        ttl = self.getTTL()
        return (ptype << 5 | ttl)

    def purgeByte(self, data):
        return [data >> 5, data & 0x1F]
