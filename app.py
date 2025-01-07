from flask import Flask, render_template, request
import mysql.connector
import numpy as np
import io
import tensorflow as tf

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',  
    'password': '',  
    'database': 'db_iris' 
}

model = tf.keras.models.load_model('./model/iris_model.h5')

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route("/add_user", methods=['POST'])
def add_user():
    try:
        nama_user = request.form['nama_user']
        foto_iris = request.files['foto_iris'].read()

        # Convert image to numpy array
        image = image.convert('RGB')  # Konversi ke RGB jika gambar tidak dalam format ini
        image = image.resize((224, 224))  # Ukuran input sesuai model
        image = np.array(image, dtype=np.float32) / 255.0  # Normalisasi
        image = np.expand_dims(image, axis=0)  # Tambahkan batch dimension

        # Predict using the model
        prediction = model.predict(image)
        predicted_class = np.argmax(prediction, axis=-1)

        # Check if the predicted class is 'eye'
        if predicted_class == 0:  # Asumsikan 0 adalah kelas untuk 'eye'
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO users (label_name, iris_image) VALUES (%s, %s)"
            cursor.execute(query, (nama_user, foto_iris))
            conn.commit()
            cursor.close()
            conn.close()

            return render_template('index.html')
        else:
            return "Error: Foto yang diunggah bukan mata. Silakan upload foto mata yang valid."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/")
def home():
    return render_template('index.html')