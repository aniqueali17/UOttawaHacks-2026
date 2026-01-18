import rpi_gpio as GPIO
import socket
import time

light_pin = 3
buzzer_pin = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(light_pin, GPIO.IN)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.output(buzzer_pin, GPIO.LOW)

is_authenticated = False

def request_login():
    global is_authenticated
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('10.56.246.143', 5000))
        resp = s.recv(1024).decode()
        is_authenticated = (resp == "AUTH_SUCCESS")
        s.close()
    except:
        is_authenticated = False

try:
    while True:
        # This will return 1 if light is above threshold, 0 if dark
        light_detected = GPIO.input(light_pin)

        if light_detected == 0 and not is_authenticated:
            #print("light=DARK. buzzer=ON")
            GPIO.output(buzzer_pin, GPIO.HIGH) # set buzzer on
        else:
            #print("light=LIGHT. buzzer=OFF", end="\r")
            GPIO.output(buzzer_pin, GPIO.LOW) # buzzer remains off

        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
