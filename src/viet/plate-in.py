# Beispiel zur Verwendung des ADXL345 Beschleunigungssensors mit Python
# Autor: Jonathan Williamson
# Lizenz: BSD (siehe LICENSE.txt in diesem Paket)

from adxl345 import ADXL345         
from math import atan2, pi      
from time import sleep              

# Initialisierung des ADXL345-Sensors
adxl345 = ADXL345()
print("ADXL345 unter Adresse 0x%x gefunden:" % (adxl345.address))

while True:
    sleep(0.5) 

    # Beschleunigungswerte entlang der Achsen abrufen
    axes = adxl345.getAxes(True) 

    # Roll- und Pitch-Winkel aus den Beschleunigungswerten berechnen
    roll = atan2(axes['z'], axes['y']) * 180 / pi + 90
    pitch = atan2(axes['z'], axes['x']) * 180 / pi + 90

    print(f"Roll: {roll:.2f}°, Pitch: {pitch:.2f}°")


