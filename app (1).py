from flask import Flask, request, jsonify, render_template
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

PAN_PIN  = 17
TILT_PIN = 27

MIN_ANGLE = 0
MAX_ANGLE = 180

pan_angle  = 90
tilt_angle = 90

GPIO.setmode(GPIO.BCM)
GPIO.setup(PAN_PIN,  GPIO.OUT)
GPIO.setup(TILT_PIN, GPIO.OUT)

pan_pwm  = GPIO.PWM(PAN_PIN,  50)
tilt_pwm = GPIO.PWM(TILT_PIN, 50)

pan_pwm.start(0)
tilt_pwm.start(0)


def angle_to_duty(angle):
    duty = 2 + (angle / 18)
    return duty


def move_servo(pwm, angle):
    duty = angle_to_duty(angle)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm.ChangeDutyCycle(0)


move_servo(pan_pwm,  pan_angle)
move_servo(tilt_pwm, tilt_angle)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/move", methods=["POST"])
def move():
    global pan_angle, tilt_angle

    data = request.get_json()

    if data is None:
        return jsonify({"error": "Ingen JSON-data skickades"}), 400

    new_pan  = data.get("pan",  pan_angle)
    new_tilt = data.get("tilt", tilt_angle)

    new_pan  = max(MIN_ANGLE, min(MAX_ANGLE, int(new_pan)))
    new_tilt = max(MIN_ANGLE, min(MAX_ANGLE, int(new_tilt)))

    move_servo(pan_pwm,  new_pan)
    move_servo(tilt_pwm, new_tilt)

    pan_angle  = new_pan
    tilt_angle = new_tilt

    print(f"Pan: {pan_angle}°  |  Tilt: {tilt_angle}°")

    return jsonify({
        "status": "ok",
        "pan":  pan_angle,
        "tilt": tilt_angle
    })


@app.route("/status")
def status():
    return jsonify({
        "pan":  pan_angle,
        "tilt": tilt_angle
    })


if __name__ == "__main__":
    try:
        print("Servern startar på http://<raspberry-pi-ip>:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        pass
    finally:
        pan_pwm.stop()
        tilt_pwm.stop()
        GPIO.cleanup()
        print("GPIO städat. Hejdå!")
