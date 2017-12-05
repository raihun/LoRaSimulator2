# -*- encoding:utf-8 -*-
from Config import Config
from Example import Example
from Network import Network
import sys
from time import sleep
from Lora import Lora


def main(argc, argv):
    config = Config()
    if argc > 1:
        print("[Start] Own-ID:{0}".format(argv[1]))
        config.setOwnid(argv[1])
    lora = Lora()
    network = Network()
    # example = Example()
    while True:
        try:
            sleep(1.0)
        except KeyboardInterrupt:
            print("Terminated.")
            break
    return


if(__name__ == "__main__"):
    main(len(sys.argv), sys.argv)
    sys.exit()
