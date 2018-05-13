from Crypto.Cipher import AES
from Crypto.Hash import MD5
import base64

class Encoder():
    # block_size
    # the block size for the cipher object; must be 16, 24, or 32 for AES
    # padding
    # the character used for padding--with a block cipher such as AES, the value
    def __init__(self, password, useBase64 = True, block_size = 32, padding = '{'):
        self.useBase64, self.block_size, self.padding = useBase64, block_size, padding
        secret = MD5.new()
        secret.update(password.encode('utf-8'))
        self.cipher = AES.new(secret.hexdigest())

    def encrypt(self, value):
        value += (self.block_size - len(value) % self.block_size) * self.padding 
        result = self.cipher.encrypt(value)
        if self.useBase64:
            result = base64.standard_b64encode(result)
        return result

    def decrypt(self, value):
        if self.useBase64:
            value = base64.b64decode(value)
        return self.cipher.decrypt(value).decode('utf-8').rstrip(self.padding)
