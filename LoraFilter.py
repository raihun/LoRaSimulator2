# -*- encoding:utf-8 -*-
from Log import Log  # Log.py


class LoraFilter:
    """
        フィルタリング用クラス
        このクラスは、エラーメッセージをネットワーククラス等に
        送らないために、存在する
    """
    def __init__(self):
        self.log = Log()
        return

    """ ES920LRから届いた受信メッセージのフィルタリング """
    def recvFilter(self, line):
        # 空行の場合
        if line == "":
            return None

        # OKの場合
        if line == "OK":
            return None

        # NGの場合
        if line.find("NG") >= 0:
            try:
                code = line.split(" ")[1]
            except IndexError:
                return None

            if code == "001":
                self.log.add("未定義コマンド", "Error")
            if code == "002":
                self.log.add("オプション値異常", "Error")
            if code == "003":
                self.log.add("FlashROM 消去異常", "Error")
            if code == "004":
                self.log.add("FlashROM 書込異常", "Error")
            if code == "005":
                self.log.add("FlashROM 読込異常", "Error")
            if code == "100":
                self.log.add("送信データ長異常", "Error")
            if code == "101":
                self.log.add("送信異常(送信中の送信要求)", "Error")
            if code == "102":
                self.log.add("送信異常(キャリアセンス検出)", "Error")
            if code == "103":
                self.log.add("ACK 未受信", "Error")
            if code == "104":
                self.log.add("送信異常(送信未完了)", "Error")
            return None

        # 上記以外の場合
        return line
