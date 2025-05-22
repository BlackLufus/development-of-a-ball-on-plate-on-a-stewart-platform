import signal, sys, time, cv2
from simple_pid import PID
from adxl345 import ADXL345
from MCP4728 import MCP4728
from math import atan2, pi
from time import sleep
from ball_tracker import BallTracker

# Sensor und DAC initialisieren
adxl345 = ADXL345()
dac_x4 = MCP4728(address=0x60, debug=True)
dac_x4.set_ext_vcc(channel=0, vcc=5.1)
dac_x4.set_ext_vcc(channel=1, vcc=5.1)
dac_x4.ch0_gain = dac_x4.ch1_gain = 1
dac_x4.ch0_pd = dac_x4.ch1_pd = 0
dac_x4.ch0_vref = dac_x4.ch1_vref = 0

# Setpoints
setpoint_ball_x = 0
setpoint_ball_y = 0
setpoint_roll = 0
setpoint_pitch = 0

# PID-Regler für Ballposition (außen) und Neigung (innen)
pid_outer_x = PID(1.4, 0.5, 0.3, output_limits=(-1, 1), setpoint=setpoint_ball_x)
pid_outer_y = PID(1.4, 0.5, 0.3, output_limits=(-1, 1), setpoint=setpoint_ball_y)
pid_inner_x = PID(1.0, 0.4, 0.4, output_limits=(-1, 1), setpoint=setpoint_roll)
pid_inner_y = PID(1.0, 0.4, 0.4, output_limits=(-1, 1), setpoint=setpoint_pitch)

# Einfacher Tiefpassfilter
class PT1Filter:
    def __init__(self, T, dt=0.005):
        self.T = T
        self.k = dt / (T + dt)
        self.y = 0
    def update(self, u):
        self.y = (1 - self.k) * self.y + self.k * u
        return self.y

# Hilfsfunktionen
def normalize(a, min_val, max_val):
    return ((a - min_val) / (max_val - min_val)) * 2 - 1

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def cleanup_and_exit(signal_received, frame, tracker):
    print("\nTerminating program. Setting DAC channels back to 2.5V...")
    dac_x4.ch0_vout = dac_x4.ch1_vout = 2.5
    dac_x4.multi_write(ch0=True, ch1=True)
    tracker.release_camera()
    cv2.destroyAllWindows()
    sys.exit(0)

x, y = 0.0, 0.0
roll_filter = PT1Filter(T=0.015)
pitch_filter = PT1Filter(T=0.015)

def main_loop():
    global x, y 
    counter = 0
    tracker = BallTracker(camera_index=1)
    signal.signal(signal.SIGINT, lambda s, f: cleanup_and_exit(s, f, tracker))
    
    try:
        while True:
            sleep(0.005)
            ball_position = tracker.get_ball_position()
            if ball_position:
                x, y = ball_position

            normalized_x = normalize(x, 0, 630)
            normalized_y = normalize(y, 0, 600)

            # Äußere PID-Regler alle 5 Zyklen
            if counter % 5 == 0 and counter > 0:
                Y_ball_X = pid_outer_x(normalized_x)
                Y_ball_Y = pid_outer_y(normalized_y)

                desired_roll =  Y_ball_X - Y_ball_Y
                desired_pitch = -Y_ball_X - Y_ball_Y

                pid_inner_x.setpoint = desired_roll
                pid_inner_y.setpoint = desired_pitch
            
            counter += 1

            # Neigungsdaten lesen und filtern
            axes = adxl345.getAxes(True)
            roll = atan2(axes['z'], axes['y']) * 180 / pi + 90
            pitch = atan2(axes['z'], axes['x']) * 180 / pi + 90

            roll = clamp(roll, -8.5, 6)
            pitch = clamp(pitch, -1, 14)

            filtered_roll = roll_filter.update(roll)
            filtered_pitch = pitch_filter.update(pitch)

            normalized_roll = normalize(filtered_roll, -8.5, 6)
            normalized_pitch = normalize(filtered_pitch, -1, 14)

            Y_Roll = pid_inner_x(normalized_roll)
            Y_Pitch = pid_inner_y(normalized_pitch)

            Volt_Roll = 2.5 * Y_Roll + 2.5
            Volt_Pitch = -2.5 * Y_Pitch + 2.5

            # DAC-Ausgänge setzen
            dac_x4.ch0_vout = Volt_Roll
            dac_x4.ch1_vout = Volt_Pitch
            dac_x4.multi_write(ch0=True, ch1=True)

            if cv2.waitKey(40) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"An error occurred: {e}")
        cleanup_and_exit(None, None, tracker)

if __name__ == "__main__":
    main_loop()

