import traceback


class ODPRC4:
    def __init__(self, password: str):
        self.constant_val = 256
        self.password = password
        self.sbox = []

    def _rc4_initialize(self):
        self.sbox = list(range(256))
        key = [ord(self.password[i % len(self.password)]) for i in range(256)]
        j = 0
        for i in range(256):
            j = (j + self.sbox[i] + key[i]) % 256
            self.sbox[i], self.sbox[j] = self.sbox[j], self.sbox[i]

    def _en_de_crypt(self, text: str) -> str:
        self._rc4_initialize()
        i = j = 0
        result = []
        for char in text:
            i = (i + 1) % 256
            j = (j + self.sbox[i]) % 256
            self.sbox[i], self.sbox[j] = self.sbox[j], self.sbox[i]
            result.append(chr(ord(char) ^ self.sbox[(self.sbox[i] + self.sbox[j]) % 256]))
        return ''.join(result)

    @staticmethod
    def _str_to_hex_str(text: str) -> str:
        return ''.join(f"{ord(char):02x}" for char in text)

    @staticmethod
    def _hex_str_to_str(hex_text: str) -> str:
        result = []
        try:
            for i in range(0, len(hex_text), 2):
                result.append(chr(int(hex_text[i:i + 2], 16)))
        except Exception as e:
            traceback.print_exc()
        return ''.join(result)

    def encrypt(self, text: str) -> str:
        return self._str_to_hex_str(self._en_de_crypt(text))

    def decrypt(self, hex_text: str) -> str:
        return self._en_de_crypt(self._hex_str_to_str(hex_text))


# Example usage
# rc4 = ODPRC4("my_secret_password")
# encrypted = rc4.encrypt("Hello")
# decrypted = rc4.decrypt(encrypted)
# print("Encrypted:", encrypted)
# print("Decrypted:", decrypted)
# rc4 = ODPRC4("INDOSAT2798")
#print(rc4.decrypt("b1789071c2776e3358fa518cb55250241d1de6beedcf9f69a43f47f59e8b1df127b6063dee143ce8f812e2dfeca4a650229f44cb168ec27dfee0dc3b00c6da9abb9700ebdb99161f0de04f570c6efadf221589e1f533a0136018b274624f4434e1a3e74c114b9957b7a52918c6aed50c55c5c8960af11d66eb3112ef28fa992c965bbaaf00b6d2f8849236d399dab0e1d608d7756defaf86c9f016dbe36e8300bcb940326fa58ee2a98bacfa1d3c813ce8ee7ca472576e9c390bc332c0d12b50670ffa155f1598a2aa88207887e9f3586c0fe1d05d04832520efc1c6129e486fa04517970eebe121a95f329605fcaacf687f2dd090bc56c0ae7ae318bf0cb45d219d3ad044a7d0a7f6e954a70e38d0960c50806a1836d28fb087c5f3a6849787bce0fce941422df270e83cb9710c9d4a710b67893b05b246c33cba9d1446c8050395069a37e121bfc00f59a6320e868a5cc6f56f1eccf303c40b042a859c5c6c30f6696b9cb02886d48a373addd4e82130df6b01938eeed14b420e84f932627e1939"))
