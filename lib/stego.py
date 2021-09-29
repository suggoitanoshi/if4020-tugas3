import random
from PIL import Image
from math import ceil,floor,log10, sqrt

class stego:
  input_file = ""
  
  def __init__(self, inputfile: str):
    """Objek generik untuk menangani Steganografi"""
    self.input_file = inputfile

  def embed(self, message: bytearray, key: bytearray):
    """Masukkan message ke dalam carrier, mengembalikan carrier yang berisi pesan"""
    pass

  def extract(self) -> str:
    """Mengeluarkan message dari carrier, mengembalikan pesan dari carrier"""
    pass

class image_stego(stego):
  MESSAGE_INFO_LENGTH = 1+32+1 # 1 bit randomize info, 1 bit encryption info, 32 bit message length info

  def __init__(self, inputfile: str):
    super().__init__(inputfile)

  # convert string to binary
  # input
  # string          : str       - ex. "abc"
  # output
  # str(bin) - ex. '011000010110001001100011'
  def string_to_bin(self,string:str) -> str:
    if string == None or len(string) == 0:
      return ""
    str_bin = ""
    for char in string:
      str_bin += format(ord(char),'08b')
    return str_bin

  # encrypt extracted message
  # input
  # message         : str(bin)  - ex. '0001001000010010'
  # key             : str       - ex. 'ab'
  # output
  # str(bin) - ex. '0111001101110000' 
  def encrypt(self,message:str,key:str) -> str:
    # convert message to binary
    message_bin = self.string_to_bin(message)

    # convert key to binary
    key_bin = self.string_to_bin(key)

    # no key
    if len(key_bin)==0:
      return message_bin
    
    # XOR Process
    if len(key_bin) > len(message_bin):
      key_bin = key_bin[0:len(message_bin)]
    elif len(key_bin) < len(message_bin):
      key_bin = (key_bin*ceil(len(message_bin)/len(key_bin)))[0:len(message_bin)]
    
    result = int(message_bin,2) ^ int(key_bin,2)
    result = '{0:b}'.format(result)
    result = ('0'*(len(message_bin)-len(result)))+result

    return result 

  # decrypt extracted message
  # input
  # ciphertext_bin  : str(bin)  - ex. '0001001000010010'
  # key             : str       - ex. 'ab'
  # output
  # str(bin) - ex. '0111001101110000'
  def decrypt(self,ciphertext_bin:str,key:str) -> str:
    key_bin = self.string_to_bin(key)
    if key==None or len(key) == 0:
      return ''.join([chr(int(ciphertext_bin[i:i+8],2)) for i in range(0, len(ciphertext_bin), 8)])

    if len(key_bin) > len(ciphertext_bin):
      key_bin = key_bin[0:len(ciphertext_bin)]
    elif len(key_bin) < len(ciphertext_bin):
      key_bin = (key_bin*ceil(len(ciphertext_bin)/len(key_bin)))[0:len(ciphertext_bin)]
    
    ciphertext_bin = [ciphertext_bin[i:i+8] for i in range(0, len(ciphertext_bin), 8)]
    key_bin = [key_bin[i:i+8] for i in range(0, len(key_bin), 8)]
    
    result = []
    for i in range(len(ciphertext_bin)):
      result.append(chr( int(ciphertext_bin[i],2) ^ int(key_bin[i],2)))
    return ''.join(result)

  # replace lsb by decreasing value by 1 to make 0 or increase value by 1 to make 1
  # input
  # org_value       : int          - ex. 35
  # key             : int (1 or 0) - ex. 0
  # output
  # int - ex. 34
  def lsb_replace(self,org_value:int,rep_value:int) -> int:
    if rep_value == '0' and (org_value % 2) != 0:
      return org_value-1
    elif rep_value == '1' and (org_value % 2) != 1:
      return org_value+1
    return org_value
  
  def embed(self, outputfile, message: str, key: str, encryption: bool, randomize: bool):
    target_image = Image.open(self.input_file,'r')

    ## Get pixel array
    pixel_array = list(target_image.copy().getdata())
    pixel_array_new = pixel_array.copy()
    pixel_tuple_length = 1

    ## Get image info
    image_pixel_type = target_image.mode    
    
    if image_pixel_type not in ["1","L","P"]: # non mono color info and converting
      # Get pixel tuple length
      pixel_tuple_length = len(pixel_array_new[0])
      # Converting list of tuple to list
      pixel_array_new = [item for t in pixel_array_new for item in t]
    image_message_capacity = len(pixel_array_new) - self.MESSAGE_INFO_LENGTH

    if image_message_capacity <= 0:
      return "IMAGE FAIL"

    ## Message Embedding
    # Message length check
    if len(message)*8 <= 0 or len(message)*8 > image_message_capacity:
      return "MESSAGE CAPACITY FAIL"
    
    # Message encrypting
    enc_message = self.encrypt(message,key) if encryption else self.string_to_bin(message)

    # message info header
    message_info_bin = "1" if randomize else "0"
    message_info_bin += "1" if encryption else "0"
    message_info_bin += format(len(enc_message),'032b')

    # set message header
    for i in range(len(message_info_bin)):
      pixel_array_new[i] = self.lsb_replace(pixel_array_new[i],message_info_bin[i])
  
    if randomize:
      # set random seed
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
      rms = sqrt(sigma_i/(target_image.size[0]*target_image.size[1]))
      psnr = 20 * log10(255/rms)
      if psnr <= 30: # PSNR too low
        return "PSNR FAIL : " + str(psnr)
    else:
      it = [iter(pixel_array_new)] * pixel_tuple_length
      pixel_array_new = list(zip(*it))

      sigma_i = [0 for i in range(pixel_tuple_length)]
      for pixel_idx in range(len(pixel_array)):
        for channel in range(len(pixel_array[pixel_idx])):
          sigma_i[channel] += (pixel_array[pixel_idx][channel]-pixel_array_new[pixel_idx][channel]) ** 2
      rms = [(sqrt(sigma_i_channel/(target_image.size[0]*target_image.size[1]))) for sigma_i_channel in sigma_i]

      psnr = ""
      
      for channel_rms in rms:
        psnr_c = 20 * log10(255/channel_rms)
        psnr += str(psnr_c) + " "
        if psnr_c <= 30: # PSNR too low
          return "PSNR FAIL : " + str(psnr_c)
    # Save result
    created_image = Image.new(mode=target_image.mode, size=target_image.size)
    created_image.putdata(pixel_array_new)
    created_image.save(outputfile)
    return "SUCCESS, PSNR : " + str(psnr)
    
  def extract(self,key) -> str:
    target_image = Image.open(self.input_file,'r')

    if target_image.size[0] == 0 or target_image.size[1] == 0:
      return "NO PIXEL DATA FOUND"
    
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

    image_message_capacity = len(pixel_array) - self.MESSAGE_INFO_LENGTH

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
    
    if encryption:
      return self.decrypt(message_bin,key)
    else:
      return ''.join([chr(int(message_bin[i:i+8],2)) for i in range(0, len(message_bin), 8)])

class audio_stego(stego):
  def __init__(self, inputfile: str):
    super().__init__(inputfile)

  def embed(self, message: str, encryption: bool, key: str, randomize: bool):
    pass

  def extract(self) -> str:
    pass