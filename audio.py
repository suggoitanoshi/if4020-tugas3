import random

class audio_stego:
  def __init__(self, carrier: bytearray, random: bool):
    """Objek untuk menangani Steganografi Audio"""
    self.__carrier = carrier
    self.__israndom = random
    self.__channel, self.__bitsample, self.datasize, self.payload = self.__getaudioinfo()

  def embed(self, message: bytearray, key: int):
    #Cek jump menurut tipe file wav (16-bit, 24-bit, 32-bit)
    jump = self.__bitsample//8
    panjangpesan = len(message)

    #Embed panjang pesan
    bytepanjang = panjangpesan.to_bytes(4, 'big')
    for i in range(0,4):
      self.__carrier[44+i] = bytepanjang[i]

    
    if(self.__israndom):
      self.__carrier[48] = 1
      usedidx = []
      random.seed(key)
      idx = random.random()
      i = 0
      bitpesan = ''
      while i < panjangpesan*8:
        if idx in usedidx:
          pass
        else:
          usedidx.append(idx)
          bitidx = i%8
          if(bitidx==0):
            bitpesan = self.__tobit(message[i//8])
            if(bitpesan[bitidx]=='0'):
              self.__carrier[idx+49] = self.__changetozero(self.__carrier[idx+49])
            else:
              self.__carrier[idx+49] = self.__changetoone(self.__carrier[idx+49])
            i += 1
          idx = random.random()
    

    else:
      self.__carrier[48] = 0
      bitpesan = ''
      for i in range(0,panjangpesan*8):
        bitidx = i%8
        if(bitidx==0):
          bitpesan = self.__tobit(message[i//8])
        if(bitpesan[bitidx]=='0'):
          self.__carrier[i+49] = self.__changetozero(self.__carrier[i+49])
        else:
          self.__carrier[i+49] = self.__changetoone(self.__carrier[i+49])   

    #X. Write file hasil
    fname = open('../teswrite.wav', 'wb')
    fname.write(self.__carrier)
    fname.close()
    #print('Done!')


  def extract(self) -> bytearray:
    #Cek jump menurut tipe file wav (16-bit, 24-bit, 32-bit)
    jump = self.__bitsample//8
    panjangpesan = int.from_bytes(self.__carrier[44:48], 'big')
    messagebytes = []
    arrtemp = [0 for i in range(0, panjangpesan)]
    messageobj = bytearray(arrtemp)
    if(self.__israndom):
      self.__carrier[48] = 1
      usedidx = []
      idx = random.seed(key)
    else:
      j = 0
      bit = ''
      for i in range(0,panjangpesan*8):
        bit += self.__tobit(self.__carrier[i+49])[7]
        j += 1
        if j==8:
          messagebytes.append(int(bit,2))
          bit = ''
          j = 0
          
    for i in range(0,len(messagebytes)):
      print(len(messagebytes))
      print(messagebytes)
      messageobj[i] = messagebytes[i]

    #X. Write file hasil
    fname = open('../hasilekstrak', 'wb')
    fname.write(messageobj)
    fname.close()
    print('Done!')
      

  def __getaudioinfo(self):
    # 2. Get basic WAV information
    # File structure:
    # 01 - 16: Type header
    # 17 - 20: Format length (16)
    # 21 - 22: Type of format
    # 23 - 24: Number of channels (2 byte int)
    # 25 - 28: Sample rate (32 bit int)
    # 29 - 32: Bytes/sec
    # 33 - 34: Block alignment
    # 35 - 36: Bits/sample
    # 37 - 40: Data header
    # 41 - 44: Data size
    channel = int.from_bytes(byte[22:23], 'little')
    bitsample = int.from_bytes(byte[34:35], 'little')
    datasize = int.from_bytes(byte[40:43], 'little')
    #print('channel:', channel)
    #print('sample :', bitsample)
    #print('size   :', datasize)

    # 3. Hitung payload
    # (Data disembunyikan di 1 bit tiap channel)
    # 32 bit pertama dipakai untuk menyatakan panjang bit pesan tersembunyi dalam byte
    # 8 bit berikutnya menentukan sekuensial atau acak
    # (0 = sekuensial, 1 = acak)
    payload = datasize//(bitsample//8) - 32 - 1
    #print('payload:', payload, "bits")

    return channel, bitsample, datasize, payload

    

  def __tobit(self, byte):
    #hasil = bin(int.from_bytes(byte, 'little'))
    hasil = bin(byte)[2:].zfill(8)
    return hasil
    
  def __changetozero(self, byte):
    tes = bin(byte)
    #tes = bin(int.from_bytes(b'\x11', byteorder=sys.byteorder))
    #print(tes)
    tes = tes[:6]
    tes = tes + '0'
    #print(tes)
    #print(int(tes, 2).to_bytes(1,'big'))
    return int(tes, 2)

  def __changetoone(self, byte):
    tes = bin(byte)
    #tes = bin(int.from_bytes(b'\x11', byteorder=sys.byteorder))
    #print(tes)
    tes = tes[:6]
    tes = tes + '1'
    #print(tes)
    #print(int(tes, 2).to_bytes(1,'big'))
    return int(tes, 2)


# TESTING
# 1. Baca file WAV ke bytearray
#file = open("../example.wav", "rb")
file = open("../teswrite.wav", "rb")
byte = bytearray(file.read()) 
file.close()


# 4. Memasukkan file
finput = open("../tespesan", "rb")
pesan = bytearray(finput.read()) 
finput.close()



audio = audio_stego(byte, False)
#audio.embed(pesan,1)
audio.extract()
