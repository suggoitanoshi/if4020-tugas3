from lib.stego import stego
import random

class audio_stego(stego):
  def __init__(self, carrier: bytearray, random: bool):
    """Objek untuk menangani Steganografi Audio"""
    self.__carrier = carrier
    self.__original = carrier
    self.__israndom = random
    self.__channel, self.__bitsample, self.__datasize, self.__payload = self.__getaudioinfo()

  def getpayload(self):
    # Untuk mengembalikan nilai payload terbesar yang dapat ditampung dalam hitungan bit
    return self.__payload

  def fidelity(self):
    # Fidelity: Kesamaan file ori dan stego dalam %
    # Semakin besar nilainya, kemiripan semakin tinggi
    # Nilai maks adalah 1 atau 100% kesamaan
    fid = 0
    for i in range(0, len(self.__carrier)):
      if self.__carrier[i] != self.__original[i]:
        fid += 1
    kesamaan = 1
    if(len(self.__carrier)!=0):
      kesamaan -= (fid/len(self.__carrier))
    return kesamaan

  def embed(self, message: bytearray, key: int) -> bytearray:
    #Cek jump menurut tipe file wav (16-bit, 24-bit, 32-bit)
    jump = self.__bitsample//8
    panjangpesan = len(message)

    #Embed panjang pesan
    bytepanjang = panjangpesan.to_bytes(4, 'big')
    for i in range(0,4*8):
      bit = self.__tobit(bytepanjang[i//8])[i%8]
      if bit == '0':
        self.__carrier[44+i] = self.__changetozero(self.__carrier[44+i])
      else:
        self.__carrier[44+i] = self.__changetoone(self.__carrier[44+i])

    if(self.__israndom):
      maxrand = self.__payload//jump
      self.__carrier[76] = self.__changetoone(self.__carrier[76])
      usedidx = []
      random.seed(key)
      idx = random.randint(0,maxrand)*jump
      i = 0
      bitpesan = ''
      while i < panjangpesan*8:
        if idx in usedidx:
          idx = random.randint(0,maxrand)*jump
        else:
          usedidx.append(idx)
          bitidx = i%8
          if(bitidx==0):
            bitpesan = self.__tobit(message[i//8])
           
          if(bitpesan[bitidx]=='0'):
            self.__carrier[idx+77] = self.__changetozero(self.__carrier[idx+77])
          else:
            self.__carrier[idx+77] = self.__changetoone(self.__carrier[idx+77])
          i += 1
          idx = random.randint(0,maxrand)*jump
    

    else:
      self.__carrier[76] = self.__changetozero(self.__carrier[76])
      bitpesan = ''
      
      for i in range(0,panjangpesan*8):
        bitidx = i%8
        if(bitidx==0):
          bitpesan = self.__tobit(message[i//8])
          #print(bitpesan)
          
        if(bitpesan[bitidx]=='0'):
          self.__carrier[i*jump+77] = self.__changetozero(self.__carrier[i*jump+77])
          
        else:
          self.__carrier[i*jump+77] = self.__changetoone(self.__carrier[i*jump+77])  
        #print('i ke',i*jump+77,':',bitpesan[bitidx])
        #print(self.__carrier[i*jump+77]) 
    
    #X. Write file hasil
    fname = open('../audioembed.wav', 'wb')
    fname.write(self.__carrier)
    fname.close()
    return self.__carrier
    #print('Done!')


  def extract(self, key) -> bytearray:
    #Cek jump menurut tipe file wav (16-bit, 24-bit, 32-bit)
    jump = self.__bitsample//8
    #panjangpesan = int.from_bytes(self.__carrier[44:48], 'big')
    bitstemp = ''
    arrtemp = [0 for i in range(0, 4)]
    bytetemp = []
    lengthobj = bytearray(arrtemp)

    for i in range(0,4*8):
      bitstemp += self.__tobit(self.__carrier[i+44])[7]
      if len(bitstemp) == 8:
        bytetemp.append(int(bitstemp,2))
        bitstemp = ''

    for i in range(0,len(bytetemp)):
      lengthobj[i] = bytetemp[i]

    panjangpesan = int.from_bytes(lengthobj, 'big')
    arrtemp = [0 for i in range(0, panjangpesan)]
    messagebytes = []
    
    messageobj = bytearray(arrtemp)
    if(self.__tobit(self.__carrier[76])[7] == '1'):
      maxrand = self.__payload//jump
      usedidx = []
      random.seed(key)
      idx = random.randint(0,maxrand)*jump
      j = 0
      bit = ''
      i = 0
      while i < panjangpesan*8:
        if idx in usedidx:
          idx = random.randint(0,maxrand)*jump
        else:
          usedidx.append(idx)
          
          bit += self.__tobit(self.__carrier[idx+77])[7]
          #print('bit',i,':',idx, '=', bit)
          j += 1
          if j==8:
            messagebytes.append(int(bit,2))
            bit = ''
            j = 0
          idx = random.randint(0,maxrand)*jump
          i += 1
    else:
      j = 0
      bit = ''
      
      for i in range(0,panjangpesan*8):
        bit += self.__tobit(self.__carrier[i*jump+77])[-1]
        #print('i ke',i,";",bit)
        j += 1
        if j==8:
          messagebytes.append(int(bit,2))
          #print(bit)
          
          bit = ''
          j = 0
          
    for i in range(0,len(messagebytes)):
      messageobj[i] = messagebytes[i]

    #X. Write file hasil
    fname = open('../hasilekstrak2', 'wb')
    fname.write(messageobj)
    fname.close()
    return messageobj
    #print('Done!')
      

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
    channel = int.from_bytes(self.__carrier[22:23], 'little')
    bitsample = int.from_bytes(self.__carrier[34:35], 'little')
    datasize = int.from_bytes(self.__carrier[40:43], 'little')
    #print('channel:', channel)
    #print('sample :', bitsample)
    #print('size   :', datasize)

    # 3. Hitung payload
    # (Data disembunyikan di 1 bit tiap channel)
    # 32 bit pertama dipakai untuk menyatakan panjang bit pesan tersembunyi dalam byte
    # 8 bit berikutnya menentukan sekuensial atau acak
    # (0 = sekuensial, 1 = acak)
    payload = (datasize - 33)//(bitsample//8)
    #print('payload:', payload, "bits")

    return channel, bitsample, datasize, payload

    

  def __tobit(self, byte):
    hasil = bin(byte)[2:].zfill(8)
    return hasil
    
  def __changetozero(self, byte):
    tes = bin(byte)
    tes = tes[:6]
    tes = tes + '0'
    return int(tes, 2)

  def __changetoone(self, byte):
    tes = bin(byte)
    tes = tes[:6]
    tes = tes + '1'
    return int(tes, 2)


# TESTING
# 1. Baca file WAV ke bytearray
file = open("../example.wav", "rb")
byte = bytearray(file.read()) 
file.close()


# 4. Memasukkan file
finput = open("../tespesan", "rb")
pesan = bytearray(finput.read()) 
finput.close()



audio = audio_stego(byte, False)
audio.embed(pesan,42)
#audio.extract(42)

print(audio.fidelity())
