# -*- encoding:utf-8 -*-
from Example import Example
from Network import Network
import sys
from time import sleep
from Lora import Lora


def main(argc, argv):
    lora = Lora()
    example = Example()
    network1 = Network()
    network2 = Network()
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
