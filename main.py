from flask import Flask, render_template, request
from flask.wrappers import Response
import os
import lib.rc4 as rc4 # implementasi RC4
import lib.stego as stego # implementasi steganografi image
import lib.audio as stegoaudio # implementasi steganografi audio

app = Flask(__name__,
  template_folder='template',
  static_url_path='',
  static_folder='static')

@app.route('/', methods=['POST', 'GET'])
def index():
  message = '' #success msg / psnr / fidelity
  if request.method == 'POST':
    jenis = request.form.get('jenis')
    if jenis == 'rc4':
      rc4key = request.form.get('rc4key')
      if request.form.get('proses') == 'enkripsi':
        if request.form.get('input') == 'papanketik':
          # Enkripsi RC4, masukan keyboard
          plainteks = request.form.get('rc4input')
          pass
        else:
          # Enkripsi RC4, masukan file
          pass
      else:
        if request.form.get('input') == 'papanketik':
          # Dekripsi RC4, masukan keyboard
          cipherteks = request.form.get('rc4input')
          message = cipherteks
          pass
        else:
          # Dekripsi RC4, masukan file
          pass
    elif jenis == 'stegoimage':
      pass
    else:
      if request.form.get('stegoenkripsi') == 'true':
        # Enkripsi pakai RC4
        pass
      carrier = bytearray(request.files['carrier'].stream.read())
      if request.form.get('proses2') == 'embed':
        pesan = bytearray(request.files['fileinput'].stream.read())
        if request.form.get('urutan') == 'acak':
          # Embed audio, urutan acak dengan key
          key = request.form.get('keystego')
          audio = stegoaudio.audio_stego(carrier, True)
          audio.embed(pesan,key)
          message = 'File sudah diembed'
        else:
          # Embed audio, urutan sekuensial
          audio = stegoaudio.audio_stego(carrier, False)
          audio.embed(pesan,0)
          message = 'File sudah diembed'
      else:
        if request.form.get('urutan') == 'acak':
          # Extract audio, urutan acak dengan key
          key = request.form.get('keystego')
          audio = stegoaudio.audio_stego(carrier, True)
          audio.extract(pesan,key)
          message = 'File sudah diextract'
        else:
          # Extract audio, urutan sekuensial
          audio = stegoaudio.audio_stego(carrier, False)
          audio.embed(pesan,0)
          message = 'File sudah diextract'
  return render_template('index.html', message=message)

@app.route('/download', methods=['POST', 'GET'])
def download():
  return Response(result, mimetype=mime)

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

if __name__ == '__main__':
  app.run(debug=True)
