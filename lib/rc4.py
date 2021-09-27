class RC4:
  def __init__(self, key: bytearray):
    """Objek untuk menangani enkripsi dan dekripsi RC4"""
    self.__key = key
    self.__KSA(bytearray([i for i in range(256)]))

  def encrypt(self, message: bytearray) -> bytearray:
    """Enkripsi pesan dengan RC4"""
    return self.__PRGA(message)

  def decrypt(self, message: bytearray) -> bytearray:
    """Dekripsi pesan dari RC4"""
    return self.__PRGA(message)

  def __KSA(self, S: bytearray):
    """Key-Scheduling Algorithm
    Fungsi ini mengisi atribut S dari object RC4 yang terbentuk
    dengan memanipulasi S yang diberikan
    """
    self.__S = [x for x in S] # copy S
    j = 0
    for i in range(256):
      j = (j + self.__S[i] + self.__key[i % len(self.__key)]) % 256
      # swap S[i] and S[j]
      tmp = self.__S[i]
      self.__S[i] = self.__S[j]
      self.__S[j] = tmp

  def __PRGA(self, message: bytearray) -> bytearray:
    """Pseudorandom Generation Algorithm - membangkitkan Keystream
    """
    j = 0
    enc = [x for x in message]
    for idx in range(len(message)):
      # get i and j
      i = (idx+1) % 256
      j = (j + self.__S[i]) % 256
      # swap i and j
      tmp = self.__S[i]
      self.__S[i] = self.__S[j]
      self.__S[j] = tmp
      # run through LFSR once
      u = self.__LFSR()
      # encrypt
      enc[idx] = enc[idx] ^ u
    return enc

  def __LFSR(self) -> int:
    """Linear Feedback Shift Register"""
    x = self.__S.pop()
    out = x ^ self.__S[254] ^ self.__S[244]
    self.__S.append(out)
    return out