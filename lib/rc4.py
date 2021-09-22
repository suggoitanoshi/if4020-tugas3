class RC4:
  def __init__(self, key: bytearray):
    """Objek untuk menangani enkripsi dan dekripsi RC4"""
    self.__key = key
    self.__KSA(bytearray([i for i in range(256)]))

  def encrypt(self, message: bytearray) -> bytearray:
    """Enkripsi pesan dengan RC4"""
    return message

  def decrypt(self, message: bytearray) -> bytearray:
    """Dekripsi pesan dari RC4"""
    return message

  def __KSA(self, S):
    """Key-Scheduling Algorithm
    Fungsi ini mengisi atribut S dari object RC4 yang terbentuk
    dengan memanipulasi S yang diberikan
    """
    self.__S = S
    pass

  def __PRGA(self) -> bytearray:
    """Pseudorandom Generation Algorithm
    Fungsi ini mengubah atribut S dari object RC4 yang terbentuk
    """
    pass