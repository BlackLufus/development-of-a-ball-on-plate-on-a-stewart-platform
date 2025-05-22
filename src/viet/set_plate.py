import signal
import sys
from simple_pid import PID
from adxl345 import ADXL345
from math import atan2, pi
from MCP4728 import MCP4728
from time import sleep

# Initialisierung des Beschleunigungssensors
adxl345 = ADXL345()
print("ADXL345 unter Adresse 0x%x gefunden:" % (adxl345.address))

# Vorgabewerte für Roll- und Pitch-Winkel (in Grad)
roll_setpoint = 0
pitch_setpoint = 7

# Falls Setpoints als Argumente übergeben wurden, übernehmen
if len(sys.argv) > 2:
    try:
        roll_setpoint = float(sys.argv[1])
        pitch_setpoint = float(sys.argv[2])
        print(f"Verwende übergebene Sollwerte: Roll = {roll_setpoint}, Pitch = {pitch_setpoint}")
    except ValueError:
        print("Ungültige Sollwerte übergeben. Verwende Standardwerte.")

# PID-Regler für Roll und Pitch konfigurieren
pidr = PID(0.08, 0.08, 0.02, setpoint=roll_setpoint)
pidp = PID(0.08, 0.08, 0.02, setpoint=pitch_setpoint)

# DAC (Digital-Analog-Wandler) initialisieren
dac_x4 = MCP4728(address=0x60, debug=True)
dac_x4.set_ext_vcc(channel=0, vcc=5.1)
dac_x4.set_ext_vcc(channel=1, vcc=5.1)

# DAC-Kanäle konfigurieren
dac_x4.ch0_gain = 1
dac_x4.ch0_pd   = 0
dac_x4.ch0_vref = 0
dac_x4.ch1_gain = 1
dac_x4.ch1_pd   = 0
dac_x4.ch1_vref = 0

# Klasse für PT1-Tiefpassfilter
class PT1Filter:
    def __init__(self, T, dt=0.04):
        self.T = T
        self.dt = dt
        self.k = dt / (T + dt)
        self.y = 0

    # Filteraktualisierung mit neuem Eingangswert
    def update(self, u):
        self.y = (1 - self.k) * self.y + self.k * u
        return self.y

# Funktion zur Rücksetzung und Beendigung bei SIGINT (Ctrl+C)
def cleanup_and_exit(signal_received, frame):
    print("\nProgramm wird beendet. Setze DAC-Ausgänge zurück auf 2.5V...")
    dac_x4.ch0_vout = 2.5
    dac_x4.ch1_vout = 2.5
    dac_x4.multi_write(ch0=True, ch1=True)
    print("DAC-Ausgänge zurückgesetzt. Beende Programm.")
    sys.exit(0)

# Signalhandler registrieren
signal.signal(signal.SIGINT, cleanup_and_exit)

# Filter für Roll und Pitch initialisieren
roll_filter = PT1Filter(T=0.2)
pitch_filter = PT1Filter(T=0.2)

# Hauptprogrammschleife
def main_loop():
    try:
        while True:
            sleep(0.04)  # Abtastrate von 25 Hz

            # Sensorwerte auslesen
            axes = adxl345.getAxes(True)

            # Winkelberechnung aus Beschleunigungswerten
            roll = atan2(axes['z'], axes['y']) * 180 / pi + 90
            pitch = atan2(axes['z'], axes['x']) * 180 / pi + 90

            # Werte filtern
            filtered_roll = roll_filter.update(roll)
            filtered_pitch = pitch_filter.update(pitch)

            # PID-Regler berechnen
            Y_R = pidr(filtered_roll)
            Y_P = pidp(filtered_pitch)

            # Spannungsberechnung und Begrenzung auf 0–5V
            VR_1 = 2.5 * Y_R + 2.5
            VR_2 = max(0, min(5, VR_1))

            VP_1 = -2.5 * Y_P + 2.5
            VP_2 = max(0, min(5, VP_1))

            # Debug-Ausgabe der Werte
            print(f"Roll = {roll:.3f}, Y_R = {Y_R:.3f}, VR_1 = {VR_1:0.3f}, VR_2 = {VR_2:0.3f}")
            print(f"Pitch = {pitch:.3f}, Y_P = {Y_P:.3f}, VP_1 = {VP_1:0.3f}, VP_2 = {VP_2:0.3f}")

            # DAC-Ausgänge setzen
            dac_x4.ch0_vout = VR_2
            dac_x4.ch1_vout = VP_2
            dac_x4.multi_write(ch0=True, ch1=True)

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        cleanup_and_exit(None, None)

# Programmstart
if __name__ == "__main__":
    main_loop()

