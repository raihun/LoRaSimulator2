# -*- encoding:utf-8 -*-
from datetime import datetime
from os import mkdir
from os.path import isdir


class Log:
    __dirname = "logs"

    def __init__(self):
        self.__checkDirectory()
        return

    @staticmethod
    def add(message, caption="Info"):
        # 1行ログ生成
        line = datetime.now().strftime("[%Y/%m/%d %H:%M:%S]\t")
        line = line + "[{0}]\t{1}\n".format(caption, message)

        # ファイル追記
        path = Log.__dirname + "/" + datetime.now().strftime("Log_%Y%m%d.txt")
        with open(path, "a") as fp:
            fp.write(line)
            fp.close()
        return

    def __checkDirectory(self):
        if(not isdir(Log.__dirname)):
            # ディレクトリ作成
            mkdir(Log.__dirname)
        return
