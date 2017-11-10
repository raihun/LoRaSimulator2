# -*- encoding:utf-8 -*-
from datetime import datetime
from os.path import exists


class Log:
    __filename = "log.txt"

    def __init__(self):
        return

    @staticmethod
    def add(message, caption="Info"):
        # 1行ログ生成
        line = datetime.now().strftime("[%Y/%m/%d %H:%M:%S]\t")
        line = line + "[{0}]\t{1}\n".format(caption, message)

        # ファイル追記
        with open(Log.__filename, "a") as fp:
            fp.write(line)
            fp.close()
        return
