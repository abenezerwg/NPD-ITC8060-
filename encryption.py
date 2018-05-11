import base64
import sys, socket, select
from Crypto.Cipher import AES
import os
import hashlib
import signal

# os.system("clear")
class encrypt:
    def hasher(self):
        email =input("Please input your email: ")
        mail=email.encode('utf-8')
        hash_object = hashlib.sha512(mail)
        hexd = hash_object.hexdigest()
        hexd_b= hexd.encode('utf-8')
        hash_object = hashlib.md5(hexd_b)
        hex_dig = hash_object.hexdigest()
        return hex_dig

    def encrypt(self,secret,data):
        BLOCK_SIZE = 32
        PADDING = '{'
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        cipher = AES.new(secret)
        encoded = EncodeAES(cipher, data)
        return encoded

    def decrypt(self,secret,data):
        data= data.decode('utf-8')
        BLOCK_SIZE = 32
        PADDING = '{'
        pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
        cipher = AES.new(secret)
        print(data)
        decoded = DecodeAES(cipher, data)
        return decoded



