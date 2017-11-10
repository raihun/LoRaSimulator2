# -*- encoding:utf-8 -*-
from Example import Example
import sys
from time import sleep
from Lora import Lora


def main(argc, argv):
    lora = Lora()
    example = Example()
    while True:
        sleep(1.0)
    return


if(__name__ == "__main__"):
    main(len(sys.argv), sys.argv)
    sys.exit()
