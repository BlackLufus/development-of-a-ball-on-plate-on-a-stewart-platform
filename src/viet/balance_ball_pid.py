import signal
import sys
from simple_pid import PID
from adxl345 import ADXL345
from MCP4728 import MCP4728
from time import sleep
import cv2
from ball_tracker import BallTracker

# ADXL345 initialisieren
adxl345 = ADXL345()
print("ADXL345 on address 0x%x:" % (adxl345.address))

# Setpoints für X und Y
x_setpoint = 315
y_setpoint = 300

if len(sys.argv) > 2:
    try:
        x_setpoint = float(sys.argv[1])
        y_setpoint = float(sys.argv[2])
        print(f"Using provided setpoints: X = {x_setpoint}, Y = {y_setpoint}")
    except ValueError:
        print("Invalid setpoint values provided. Using default values.")

# PID Setup für X und Y
pid_x = PID(0.8, 0.6, 0.65, setpoint=x_setpoint)
pid_y = PID(0.8, 0.6, 0.65, setpoint=y_setpoint)

# DAC Initialisierung
dac_x4 = MCP4728(address=0x60, debug=True)
dac_x4.set_ext_vcc(channel=0, vcc=5.1)
dac_x4.set_ext_vcc(channel=1, vcc=5.1)
dac_x4.ch0_gain = 1
dac_x4.ch0_pd = 0
dac_x4.ch0_vref = 0
dac_x4.ch1_gain = 1
dac_x4.ch1_pd = 0
dac_x4.ch1_vref = 0

def cleanup_and_exit(signal_received, frame, tracker):
    print("\nTerminating program. Setting DAC channels back to 2.5V...")
    dac_x4.ch0_vout = 2.5
    dac_x4.ch1_vout = 2.5
    dac_x4.multi_write(ch0=True, ch1=True)
    tracker.release_camera()
    cv2.destroyAllWindows()
    print("DAC channels reset. Exiting.")
    sys.exit(0)

x, y = 0.0, 0.0

def main_loop():
    global x, y 
    tracker = BallTracker(camera_index=1)
    signal.signal(signal.SIGINT, lambda signal_received, frame: cleanup_and_exit(signal_received, frame, tracker))
    
    try:
        while True:
            sleep(0.01)
            ball_position = tracker.get_ball_position()
            if ball_position:
                x, y = ball_position

            # PID berechnungen für X und Y
            Y_X = pid_x(x)/315
            Y_Y = pid_y(y)/300

            # Ausgangsspannungen für die Kanäle berechnen
            VX_1 = 2.5 + 2.5 * Y_X - 2.5 * Y_Y
            VY_1 = 2.5 + 2.5 * Y_X + 2.5 * Y_Y

            # Begrenzen der Ausgangsspannungen
            VX_2 = max(0, min(5, VX_1))
            VY_2 = max(0, min(5, VY_1))

            print(f"X = {x:.3f}, Y = {y:.3f}, Y_X = {Y_X:.3f}, Y_Y = {Y_Y:.3f}")
            print(f"VCh1 = {VX_2:.3f} V, VCh2 = {VY_2:.3f} V")

            # DAC Ausgänge setzen
            dac_x4.ch0_vout = VX_2
            dac_x4.ch1_vout = VY_2
            dac_x4.multi_write(ch0=True, ch1=True)

            # Beenden mit 'q'
            if cv2.waitKey(40) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"An error occurred: {e}")
        cleanup_and_exit(None, None, tracker)

if __name__ == "__main__":
    main_loop()

