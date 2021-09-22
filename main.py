from flask import Flask, render_template, request
from flask.wrappers import Response

import lib.rc4 as rc4 # implementasi RC4
import lib.stego as stego # implementasi beragam teknik steganografi

app = Flask(__name__,
  template_folder='template',
  static_url_path='',
  static_folder='static')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/rc4', methods=['POST'])
def operate_rc4():
  key = request.form['key']
  file = request.files['file']
  rc4_instance = rc4.RC4(file.stream.read(), bytearray(key, 'utf-8'))
  if request.form['op'] == 'encrypt':
    return rc4_instance.encrypt()
  elif request.form['op'] == 'decrypt':
    return rc4_instance.decrypt()

@app.route('/stego/image/<op>', methods=['POST'])
def image_stego(op):
  # get all request data
  image = request.files['image']
  message = request.files['message']
  stego_key = request.form['stego_key']
  msg_encrypted = request.form['is_encrypted'] == 'yes'
  encryption_key = request.form['enc_key']
  print(op)

  # make stego object and optionally RC4 object
  stego_instance = stego.image_stego(image.stream.read())
  if msg_encrypted:
    rc4_instance = rc4.RC4(encryption_key)

  if op == 'embed':
    # embed message into carrier, optionally encrypting the message before
    if msg_encrypted:
      message = rc4_instance.encrypt(message)
    result = stego_instance.embed(message, stego_key)
    mime = image.mimetype
  elif op == 'extract':
    # extract message from carrier, optionally decrypting the message after
    result = stego_instance.extract()
    if msg_encrypted:
      result = rc4_instance.decrypt()
    mime='text/plain'
  return Response(result, mimetype=mime)
