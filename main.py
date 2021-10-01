from flask import Flask, render_template, request
from flask.wrappers import Response
import os
import lib.rc4 as rc4 # implementasi RC4
import lib.stego as stego # implementasi steganografi image
import lib.audio as stegoaudio # implementasi steganografi audio
import base64

app = Flask(__name__,
  template_folder='template',
  static_url_path='',
  static_folder='static')

@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory('/home/name/Music/', path=filename)

@app.route('/', methods=['POST', 'GET'])
def index():
  message = '' #success msg / psnr / fidelity
  fileb64 = None
  rc4output = None
  isaudio = ''
  mime='application/octet-stream'
  if request.method == 'POST':
    jenis = request.form.get('jenis')
    if jenis == 'rc4':
      rc4key = request.form.get('rc4key')
      rc4i = rc4.RC4(bytearray(rc4key, 'utf-8'))
      if request.form.get('input') == 'papanketik':
        inmessage = bytearray(request.form.get('rc4input'), 'utf-8')
      else:
        inmessage = bytearray(request.files.get('fileinput').stream.read())
      if request.form.get('proses') == 'enkripsi':
        if request.form.get('input') == 'papanketik':
          # Enkripsi RC4, masukan keyboard
          rc4output = bytes(rc4i.encrypt(inmessage))
        else:
          # Enkripsi RC4, masukan file
          fileb64 = base64.b64encode(bytes(rc4i.encrypt(inmessage))).decode()
          message = 'Success encrypt file'
      else:
        if request.form.get('input') == 'papanketik':
          # Dekripsi RC4, masukan keyboard
          rc4output = bytes(rc4i.decrypt(inmessage))
        else:
          # Dekripsi RC4, masukan file
          fileb64 = base64.b64encode(bytes(rc4i.decrypt(inmessage))).decode()
          message = 'Success decrypt file'
    elif jenis == 'stegoimage':
      acak = request.form.get('urutan') == 'acak'
      encrypt = request.form.get('stegoenkripsi') == 'true'
      key = bytearray(request.form.get('keystego'), 'utf-8')
      ims = stego.image_stego(request.files.get('carrier').stream)
      msg = bytearray(request.files.get('fileinput').stream.read())
      if request.form.get('proses2') == 'embed':
        mime = request.files.get('carrier').mimetype
        rms, result = ims.embed('tmp', msg, key, encrypt, acak)
        message = f'Success embed message, RMS = {rms}'
        fileb64 = base64.b64encode(result).decode()
      else:
        result = ims.extract(key)
        message = f'Success extract message'
        fileb64 = base64.b64encode(result).decode()
    else:
      key = request.form.get('keystego')
      pesan = bytearray(request.files['fileinput'].stream.read())
      carrier = bytearray(request.files['carrier'].stream.read())
      # Cek payload
      tes = stegoaudio.audio_stego(carrier, True)
      payload = tes.getpayload()
      besarpesan = len(pesan)
      if request.form.get('stegoenkripsi') == 'true':
        rc4i = rc4.RC4(key)
      if(besarpesan>payload//8):
        return render_template('index.html', message='File carrier tidak cukup', filebin=fileb64, rc4output=rc4output, filemime=mime)
      else:
        if request.form.get('proses2') == 'embed':
          if request.form.get('stegoenkripsi') == 'true':
            # Enkripsi dulu pakai RC4
            message = rc4i.encrypt(pesan)
          if request.form.get('urutan') == 'acak':
            # Embed audio, urutan acak dengan key
            isaudio = 'true'
            audio = stegoaudio.audio_stego(carrier, True)
            fileb64 = base64.b64encode(audio.embed(pesan,key)).decode()
            message = 'File sudah diembed. Fidelity: ' + str(audio.getfidelity())
          else:
            # Embed audio, urutan sekuensial
            isaudio = 'true'
            audio = stegoaudio.audio_stego(carrier, False)
            fileb64 = base64.b64encode(audio.embed(pesan,0)).decode()
            message = 'File sudah diembed. Fidelity: ' + str(audio.getfidelity())
        else:
          if request.form.get('urutan') == 'acak':
            # Extract audio, urutan acak dengan key
            audio = stegoaudio.audio_stego(carrier, True)
            extracted = audio.extract(key)
            message = 'File sudah diextract'
          else:
            # Extract audio, urutan sekuensial
            audio = stegoaudio.audio_stego(carrier, False)
            extracted = audio.extract(0)
            message = 'File sudah diextract'
          if request.form.get('stegoenkripsi') == 'true':
            extracted = rc4i.decrypt(extracted)
          fileb64 = base64.b64encode(extracted).decode()
  return render_template('index.html', isaudio=isaudio, message=message, filebin=fileb64, rc4output=rc4output, filemime=mime)

if __name__ == '__main__':
  app.run(debug=True)
