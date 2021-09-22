class stego:
  def __init__(self, carrier: bytearray):
    """Objek generik untuk menangani Steganografi"""
    self.__carrier = carrier
  def embed(self, message: bytearray, key: bytearray) -> bytearray:
    """Masukkan message ke dalam carrier, mengembalikan carrier yang berisi pesan"""
    pass
  def extract(self) -> bytearray:
    """Mengeluarkan message dari carrier, mengembalikan pesan dari carrier"""
    pass

class image_stego(stego):
  def __init__(self, carrier: bytearray) -> stego:
    """Objek untuk menangani Steganografi Citra"""
    super().__init__(carrier)
  def embed(self, message: bytearray, key: bytearray):
    pass
  def extract(self):
    pass

class audio_stego(stego):
  def __init__(self, carrier: bytearray, random: bool):
    """Objek untuk menangani Steganografi Citra"""
    super().__init__(carrier)
  def embed(self, message: bytearray, key: bytearray):
    pass
  def extract(self) -> bytearray:
    pass