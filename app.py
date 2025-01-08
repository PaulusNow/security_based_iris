from flask import Flask, render_template, request
import mysql.connector
from PIL import Image
import numpy as np
import tensorflow as tf
from io import BytesIO
import os  # Import os untuk mengelola path dan folder

app = Flask(__name__)

# Konfigurasi database
db_config = {
    'host': 'localhost',
    'user': 'root',  
    'password': '',  
    'database': 'iris' 
}

# Load model
model = tf.keras.models.load_model('./model/iris_model.h5')

# Fungsi untuk koneksi database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Route untuk menambahkan user
@app.route("/add_user", methods=['POST'])
def add_user():
    try:
        # Ambil data dari form
        nama_user = request.form['nama_user']
        foto_iris = request.files['foto_iris']

        # Baca gambar yang diupload dan konversi ke objek PIL Image
        image = Image.open(BytesIO(foto_iris.read()))

        # Simpan gambar ke folder upload sebelum diubah ke array NumPy
        upload_dir = 'upload'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Path untuk menyimpan gambar
        image_path = os.path.join(upload_dir, foto_iris.filename)
        image.save(image_path)  # Simpan gambar ke folder upload

        # Konversi gambar ke numpy array untuk prediksi
        image = image.convert('RGB')  # Konversi ke RGB jika belum
        image = image.resize((224, 224))  # Resize ke ukuran yang sesuai dengan model
        image = np.array(image, dtype=np.float32) / 255.0  # Normalisasi nilai pixel
        image = np.expand_dims(image, axis=0)  # Tambahkan dimensi batch

        # Prediksi menggunakan model
        prediction = model.predict(image)
        predicted_class = np.argmax(prediction, axis=-1)

        # Cek apakah kelas yang diprediksi adalah 'eye'
        if predicted_class == 0:  # Asumsikan 0 adalah kelas untuk 'eye'
            # Simpan path gambar ke database
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO users (label_name, iris_image) VALUES (%s, %s)"
            cursor.execute(query, (nama_user, image_path))  # Simpan path gambar, bukan binary data
            conn.commit()
            cursor.close()
            conn.close()

            return render_template('index.html')
        else:
            return "Error: Foto yang diunggah bukan mata. Silakan upload foto mata yang valid."
    except Exception as e:
        return f"Error: {str(e)}"

# Route untuk halaman utama
@app.route("/")
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)