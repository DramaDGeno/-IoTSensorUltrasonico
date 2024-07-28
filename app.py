from flask import Flask, jsonify, send_from_directory, request
import RPi.GPIO as GPIO
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

app = Flask(__name__)

TRIGGER_PIN = 23
ECHO_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

last_email_sent = None  # Variable para rastrear el último correo enviado

def medir_distancia():
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, False)

    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        end_time = time.time()

    elapsed_time = end_time - start_time
    distancia = (elapsed_time * 34300) / 2  # Velocidad del sonido: 34300 cm/s

    return distancia

def send_email(fechaHoraActual):
    sender_email = "hidrainmatic@gmail.com"
    receiver_email = "dnamm028@gmail.com"
    password = "xmxc fxoo kfvg xnon"

    subject = "¡ADVERTENCIA! El agua bajo a niveles criticos."
    body = f"""
    <html>
        <body>
            <p>Se registró una disminución de agua a las {fechaHoraActual}</p>
            <img src="cid:alerta">
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    # Adjuntar la imagen
    with open('alerta.png', 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<alerta>')
        img.add_header('Content-Disposition', 'inline', filename='alerta.png')
        msg.attach(img)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

@app.route('/')
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route('/distancia', methods=['GET'])
def get_distancia():
    distancia = medir_distancia()
    return jsonify({'distancia': distancia})

@app.route('/send-email', methods=['POST'])
def handle_send_email():
    global last_email_sent
    data = request.json
    fechaHoraActual = data.get('fechaHoraActual')

    # Si la distancia llega a 24, envía un correo (solo una vez por cada vez que la distancia baja a 24)
    if last_email_sent is None or last_email_sent != fechaHoraActual:
        send_email(fechaHoraActual)
        last_email_sent = fechaHoraActual

    return jsonify({'success': True})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        GPIO.cleanup()
