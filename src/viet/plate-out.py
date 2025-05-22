from MCP4728 import MCP4728
import time

# DAC initialisieren
dac_x4 = MCP4728(address=0x60, debug=True)

# Externe Vcc für beide Kanäle setzen
dac_x4.set_ext_vcc(channel=0, vcc=5.1)
dac_x4.set_ext_vcc(channel=1, vcc=5.1)
print(dac_x4.ch0_ext_vcc, dac_x4.ch1_ext_vcc)

# Kanal-Konfiguration
dac_x4.ch0_gain = 1
dac_x4.ch0_pd = 0
dac_x4.ch0_vref = 0
dac_x4.ch1_gain = 1
dac_x4.ch1_pd = 0
dac_x4.ch1_vref = 0

while True:
    # Benutzereingabe für Spannungen
    u = input("Spannungen (z.B. 2.5/3.3): ")
    if u == "":
        break
    u = [float(uu.replace(",", ".")) for uu in u.split("/")]
    
    # Setze Spannungen
    dac_x4.ch0_vout = u[0]
    dac_x4.ch1_vout = u[1]
    dac_x4.multi_write(ch0=True, ch1=True)

# Setze beide Kanäle auf 2.5V und beende
print("Setze Ausgänge auf 2.5V")
dac_x4.ch0_vout = 2.5
dac_x4.ch1_vout = 2.5
dac_x4.multi_write(ch0=True, ch1=True)


