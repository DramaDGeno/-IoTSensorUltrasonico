from flask import Flask, jsonify, send_from_directory
import RPi.GPIO as GPIO
import time
import os

app = Flask(__name__)

# Configuraciones del sensor
TRIGGER_PIN = 23
ECHO_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def medir_distancia():
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)  # 10 microsegundos
    GPIO.output(TRIGGER_PIN, False)
    
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()
        
    while GPIO.input(ECHO_PIN) == 1:
        end_time = time.time()
        
    elapsed_time = end_time - start_time
    distancia = (elapsed_time * 34300) / 2  # Velocidad del sonido: 34300 cm/s
    
    return distancia

@app.route('/')
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route('/distancia', methods=['GET'])
def get_distancia():
    distancia = medir_distancia()
    return jsonify({'distancia': distancia})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        GPIO.cleanup()