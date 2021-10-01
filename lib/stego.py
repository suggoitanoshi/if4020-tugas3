import random
from typing import BinaryIO, Tuple
import io
from lib.rc4 import RC4
from PIL import Image
from math import log10, sqrt

class stego:
  input_file = ""
  
  def __init__(self, carrier: BinaryIO):
    """Objek generik untuk menangani Steganografi"""
    self.input_file = carrier 
    self.__carrier = carrier

  def embed(self, message: bytearray, key: bytearray):
    """Masukkan message ke dalam carrier, mengembalikan carrier yang berisi pesan"""
    pass

  def extract(self) -> str:
    """Mengeluarkan message dari carrier, mengembalikan pesan dari carrier"""
    pass

class image_stego(stego):
  MESSAGE_INFO_LENGTH = 1+32+1 # 1 bit randomize info, 1 bit encryption info, 32 bit message length info

  def __init__(self, inputfile: BinaryIO):
    super().__init__(inputfile)

  def ba_to_bitstring(self,ba:bytearray)->str:
    """
    Convert bytearray to string of bits
    """
    res = []
    for i in ba:
        res.append(format(i,'08b'))
    return ''.join(res)

  def bitstring_to_ba(self,bs:str)->bytearray:
    """
    Convert string of bits to bytearray
    """
    return bytearray(int(bs,2).to_bytes(length=len(bs)//8,byteorder='big'))

  
  def lsb_replace(self,org_value:int,rep_value:int) -> int:
    """
    replace lsb by decreasing value by 1 to make 0 or increase value by 1 to make 1
    input
    org_value       : int          - ex. 35
    key             : int (1 or 0) - ex. 0
    output
    int - ex. 34
    """
    if rep_value == '0' and (org_value % 2) != 0:
      return org_value-1
    elif rep_value == '1' and (org_value % 2) != 1:
      return org_value+1
    return org_value
  
  def embed(self, outputfile: str, message: bytearray, key: bytearray, encryption: bool, randomize: bool) -> Tuple[float, bytes]:
    target_image = Image.open(self.input_file)

    # Get pixel array
    pixel_array = list(target_image.copy().getdata())
    pixel_array_new = pixel_array.copy()
    pixel_tuple_length = 1

    # Get image info
    image_pixel_type = target_image.mode    
    
    if image_pixel_type not in ["1","L","P"]: 
      # Non mono color info and converting array of tuples
      pixel_tuple_length = len(pixel_array_new[0])
      pixel_array_new = [item for t in pixel_array_new for item in t]
    image_message_capacity = len(pixel_array_new) - self.MESSAGE_INFO_LENGTH

    if image_message_capacity <= 0:
      raise Exception("FAIL : EMPTY IMAGE PIXELS")

    # Message length check
    if len(message)*8 <= 0 or len(message)*8 > image_message_capacity:
      raise Exception("FAIL : MESSAGE CAPACITY")
    
    # Message encrypting
    if encryption:
      rc = RC4(key)
      enc_message = self.ba_to_bitstring(rc.encrypt(message))
    else:
      enc_message = self.ba_to_bitstring(message)

    # Creating message header
    message_info_bin = "1" if randomize else "0"        # Random mark
    message_info_bin += "1" if encryption else "0"      # Encryption mark
    message_info_bin += format(len(enc_message),'032b') # Message Length mark

    # Embedding message header
    for i in range(len(message_info_bin)):
      pixel_array_new[i] = self.lsb_replace(pixel_array_new[i],message_info_bin[i])

    # Embedding message
    if randomize:
      random.seed(key)
      
      history = []
      for i in range(len(enc_message)):
        gen_idx = self.MESSAGE_INFO_LENGTH + random.randint(0,image_message_capacity - 1)

        while gen_idx in history:
          gen_idx = self.MESSAGE_INFO_LENGTH + random.randint(0,image_message_capacity - 1)

        history.append(gen_idx)
        
        pixel_array_new[gen_idx] = self.lsb_replace(pixel_array_new[gen_idx],enc_message[i])
    else:
      for i in range(len(enc_message)):
        pixel_array_new[self.MESSAGE_INFO_LENGTH + i] = self.lsb_replace(pixel_array_new[self.MESSAGE_INFO_LENGTH + i],enc_message[i])
      
    
    # PSNR check
    if image_pixel_type in ["1","L","P"]:
      if image_pixel_type == "1":
        for i in range(len(pixel_array_new)):
          if pixel_array_new[i] == 255 - 1: # originally 1, replaced by 0
            pixel_array_new[i] = 0
          elif pixel_array_new[i] == 0 + 1: # originally 0, replaced by 1
            pixel_array_new[i] = 255
      sigma_i = 0
      for i in range(len(pixel_array)):
        sigma_i += (pixel_array[i]-pixel_array_new[i]) ** 2
      if (sigma_i==0):
        # Embedded image has no difference with original image
        # psnr = -1
        return self.embed_result(target_image.format,target_image.mode,target_image.size,pixel_array_new,None)
      rms = sqrt(sigma_i/(target_image.size[0]*target_image.size[1]))
      psnr = 20 * log10(255/rms)
      if psnr <= 30: # PSNR too low
        raise Exception("FAIL : PSNR < 30 : PSNR = " + str(psnr))
    else:
      it = [iter(pixel_array_new)] * pixel_tuple_length
      pixel_array_new = list(zip(*it))

      sigma_i = [0 for i in range(pixel_tuple_length)]
      for pixel_idx in range(len(pixel_array)):
        for channel in range(len(pixel_array[pixel_idx])):
          sigma_i[channel] += (pixel_array[pixel_idx][channel]-pixel_array_new[pixel_idx][channel]) ** 2
      for sig in sigma_i:
        if (sig==0):
          # Embedded image has no difference with original image
          # psnr = -1
          return self.embed_result(target_image.format,target_image.mode,target_image.size,pixel_array_new,None)

      rms = [(sqrt(sigma_i_channel/(target_image.size[0]*target_image.size[1]))) for sigma_i_channel in sigma_i]

      psnr = ""
      
      for channel_rms in rms:
        psnr_c = 20 * log10(255/channel_rms)
        psnr += str(psnr_c) + " "
        if psnr_c <= 30: # PSNR too low
          raise Exception("FAIL : PSNR < 30 : PSNR = " + str(psnr))
    
    # Save result
    return self.embed_result(target_image.format,target_image.mode,target_image.size,pixel_array_new,psnr)
    
  def extract(self, key: bytearray) -> bytearray:
    target_image = Image.open(self.input_file,'r')

    # Pixel data check
    if target_image.size[0] == 0 or target_image.size[1] == 0:
      raise Exception("FAIL : NO PIXEL DATA FOUND")
    
    # Get pixel array
    pixel_array = list(target_image.copy().getdata())
    if target_image.mode not in ["1","L","P"]:
      pixel_array = [item for t in pixel_array for item in t]
    # Get message info
    message_info = ""
    for i in range(self.MESSAGE_INFO_LENGTH):
      message_info += "1" if pixel_array[i] % 2 == 1 else "0"
    randomize = bool(int(message_info[0]))
    encryption = bool(int(message_info[1]))
    message_length = int(message_info[2:],2)

    # Calculate max idx
    image_message_capacity = len(pixel_array) - self.MESSAGE_INFO_LENGTH

    # Extracting binary
    message_bin = ""
    if randomize:
      history = []
      random.seed(key)
      for i in range(message_length):
        gen_idx = self.MESSAGE_INFO_LENGTH + random.randint(0,image_message_capacity - 1)

        while gen_idx in history:
          gen_idx = self.MESSAGE_INFO_LENGTH + random.randint(0,image_message_capacity - 1)

        history.append(gen_idx)

        message_bin += "1" if pixel_array[gen_idx] % 2 == 1 else "0"
    else:
      for i in range(message_length):
        message_bin += "1" if pixel_array[self.MESSAGE_INFO_LENGTH+i] % 2 == 1 else "0"
    
    # Returning extracted message
    if encryption:
      rc = RC4(key)                
      return rc.decrypt(self.bitstring_to_ba(message_bin))
    else:
      return self.bitstring_to_ba(message_bin)

  def embed_result(self,format,mode,size,data,psnr):
    """
    Save embedding result with the given format, mode, size, data, and psnr
    """
    created_image = Image.new(mode=mode, size=size)
    created_image.putdata(data)
    bytesout = io.BytesIO()
    created_image.save(bytesout, format=format)

    return psnr, bytesout.getvalue()
