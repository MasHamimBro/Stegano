from flask import Flask, render_template, request, send_from_directory
from stegano import lsb
import os

app = Flask(__name__)

def konversiascii(input_string):
    ascii_values = []
    for char in input_string:
        ascii_value = ord(char)
        ascii_values.append(ascii_value)
    return ascii_values

def konversibiner(ascii_values):
    binary_values = []
    for value in ascii_values:
        binary_value = bin(value)[2:]
        binary_values.append(binary_value)
    return binary_values

def xor_biner(binary_values_string, binary_values_key):
    result_biner = []
    for i in range(min(len(binary_values_string), len(binary_values_key))):
        result = int(binary_values_string[i], 2) ^ int(binary_values_key[i], 2)
        result_biner.append(bin(result)[2:])
    return result_biner

def biner_ke_desimal(hasil_xor):
    desimal_values = []
    for value in hasil_xor:
        desimal_value = int(value, 2)
        desimal_values.append(desimal_value)
    return desimal_values

def kodeascii(hasil_desimal):
    karakter_values = ''
    for value in hasil_desimal:
        karakter_value = chr(value)
        karakter_values += karakter_value
    return karakter_values

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hasil', methods=['POST'])
def hasil():
    input_string = request.form['input_string']
    key = request.form['key']

    ascii_values_string = konversiascii(input_string)
    ascii_values_key = konversiascii(key)

    hasil_string = konversibiner(ascii_values_string)
    hasil_key = konversibiner(ascii_values_key)

    hasil_xor = xor_biner(hasil_string, hasil_key)

    hasil_desimal = biner_ke_desimal(hasil_xor)

    hasil_karakter = kodeascii(hasil_desimal)

    return render_template('hasil.html', input_string=input_string, key=key,
                           ascii_values_string=ascii_values_string, ascii_values_key=ascii_values_key,
                           hasil_string=hasil_string, hasil_key=hasil_key,
                           hasil_xor=hasil_xor, hasil_desimal=hasil_desimal,
                           hasil_karakter=hasil_karakter)

if __name__ == '__main__':
    app.run(debug=True)

def encrypt_xor(message, key):
    message = message.upper()
    key = key.upper()

    if len(message) != len(key):
        error_message = "Panjang kunci harus sama dengan panjang teks."
        return render_template('index.html', error=error_message)

    encrypted_text = ''

    for i in range(len(message)):
        if message[i].isalpha():
            message_char = ord(message[i]) - ord('A')
            key_char = ord(key[i]) - ord('A')

            # Menggunakan operasi XOR
            encrypted_char = message_char ^ key_char
            encrypted_text += chr(encrypted_char + ord('A'))
        else:
            encrypted_text += message[i]

    return encrypted_text

@app.route('/')
def home():
    return render_template('index.html', message=None, download_link=None, encrypted_message=None)

@app.route('/hasil', methods=['POST'])
def encode():
    if 'image' not in request.files or 'message' not in request.form or 'key' not in request.form:
        return 'Invalid request'

    image = request.files['image']
    message = request.form['message']
    key = request.form['key']

    # Cek panjang pesan dan kunci
    if len(message) != len(key):
        error_message = "Panjang kunci harus sama dengan panjang pesan."
        return render_template('index.html', error=error_message)

    # Enkripsi pesan menggunakan XOR
    encrypted_message = encrypt_xor(message, key)

    # Simpan gambar yang diupload
    image_path = 'uploads/' + image.filename
    image.save(image_path)

    # Sembunyikan pesan yang telah dienkripsi dalam gambar
    secret_message = encrypted_message
    secret_image = lsb.hide(image_path, secret_message)
    secret_image_filename = 'secret_' + image.filename
    secret_image_path = 'uploads/' + secret_image_filename
    secret_image.save(secret_image_path)

    # Tautan unduh
    download_link = f'/download/{secret_image_filename}'

    return render_template('index.html', message='Proses Berhasil!', download_link=download_link, encrypted_message=encrypted_message)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=True)
