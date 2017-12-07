# -*- encoding:utf-8 -*-

from base64 import b64decode, b64encode
from binascii import a2b_hex
from Crypto.Cipher import AES
from hashlib import md5, sha256


class Encrypt:
    def encrypt(self, message, key, iv):
        # 暗号化準備
        key = sha256(key.encode()).digest()
        iv = md5(iv.encode()).digest()
        crypto = AES.new(key, AES.MODE_CBC, iv)

        # メッセージ準備
        message = b64encode(message.encode())
        for i in range(16 - len(message) % 16):
            message += "_".encode()

        # 暗号化
        return crypto.encrypt(message).hex()

    def decrypt(self, message, key, iv):
        # 復号準備
        key = sha256(key.encode()).digest()
        iv = md5(iv.encode()).digest()
        crypto = AES.new(key, AES.MODE_CBC, iv)

        # メッセージ準備
        cipher_data = a2b_hex(message)

        # 復号
        buf = crypto.decrypt(cipher_data)
        data = buf.split("_".encode())[0]
        return b64decode(data).decode()

"""
# 使い方例
if __name__ == "__main__":
    enc = Encrypt()
    encdata = enc.encrypt("こんにちは", "password", "projectone")
    print(encdata)
    decdata = enc.decrypt(encdata, "password", "projectone")
    print(decdata)
"""
