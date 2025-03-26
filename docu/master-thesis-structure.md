# Struktur für die Masterarbeit (Leitfaden)

## 1. Einleitung
### Hintergrund
Kurze Einführung in Stewart-Plattformen, ihre Anwendungen (Flugsimulatoren, Robotik, etc.) und Relevanz in der Forschung.

### Problemstellung
Warum ist die Steuerung einer Stewart-Plattform komplex? Welche Herausforderungen gibt es bei der Integration von RL?

### Ziel der Arbeit
- Programmierung der Basisplattform (Inverse Kinematik, Echtzeitsteuerung).
- Erweiterung um Nunchuk-Steuerung.
- Aufbau einer zweiten Plattform mit RL-gesteuerter Ballbalancierung.

### Aufbau der Arbeit
Kurzer Überblick über die Kapitel.

---

## 2. Theoretische Grundlagen
### Stewart-Plattform
- Mechanischer Aufbau (6 DoF, parallele Kinematik).
- Vorwärts-/Inverse Kinematik (mathematische Herleitung).
- Grenzen der Bewegung (Arbeitsraum, Singularitäten).

### Steuerungstechnik
- PID-Regelung (Grundprinzipien, warum für die Basissteuerung?).
- Echtzeitkommunikation mit Aktoren (z. B. über Arduino/ROS).

### Reinforcement Learning (RL)
- Grundkonzepte (Agent, Umwelt, Reward-Funktion).
- Algorithmus-Auswahl (z. B. PPO, DQN) und Begründung.
- Sim-to-Real-Transfer (Wie trainiert man im Simulator und überträgt auf die reale Plattform?).

---

## 3. Implementierung der Basis-Stewart-Plattform
### Hardware-Setup
- Beschreibung der vorhandenen Plattform (Aktoren, Sensoren, Mikrocontroller).
- Kommunikationsprotokolle (z. B. PWM, CAN-Bus).

### Software-Architektur
- Implementierung der inversen Kinematik (Code-Beispiele, Simulation in MATLAB/Python).
- Kalibrierung der Aktoren (Homing, Längenkorrektur).
- Echtzeitsteuerung (Loop-Rate, Latenzoptimierung).

### Ergebnisse
- Plattform bewegt sich präzise in vordefinierten Mustern.
- Diskussion von Fehlerquellen (z. B. mechanisches Spiel, Rechenungenauigkeiten).

---

## 4. Integration der Nunchuk-Steuerung
### Hardware-Anbindung
- Nunchuk-Protokolle (I2C, SPI) und Anbindung an den Mikrocontroller.
- Signalverarbeitung (Joystick-Daten, Beschleunigungssensor).

### Software-Mapping
- Übersetzung der Nunchuk-Eingaben in Plattform-Bewegungen (z. B. Joystick → Rotation, Beschleunigungssensor → Translation).
- Filterung der Eingabedaten (Rauschunterdrückung, Glättung).

### Ergebnisse
- Nutzerstudie zur Bedienerfreundlichkeit.
- Latenzmessungen und Stabilität der Steuerung.

---

## 5. Aufbau der zweiten Plattform mit RL-gesteuerter Ballbalancierung
### Mechanische Erweiterung
- Konstruktion der oberen Plattform (Material, Sensoren für Ballposition, z. B. Kamera/OpenCV oder Neigungssensoren).

### RL-Modellentwicklung
- Zustandsraum (Ballposition, Geschwindigkeit, Plattformneigung).
- Aktionen (Neigungskommandos an die Stewart-Plattform).
- Reward-Funktion (Belohnung für zentrierten Ball, Strafe für Abweichungen).

### Training und Implementierung
- Simulation in PyBullet/Gazebo zur Vorab-Training.
- Feinabstimmung am realen System (Domain Randomization, Transfer Learning).

### Ergebnisse
- Vergleich von RL mit klassischer Regelung (PID).
- Stabilitätsanalyse (Wie lange bleibt der Ball in der Mitte?).

---

## 6. Diskussion
### Kritische Reflexion
- Limitationen der Nunchuk-Steuerung (z. B. menschliche Reaktionszeit vs. RL).
- Herausforderungen beim Sim-to-Real-Transfer (z. B. unmodellierte Reibung).

### Offene Fragen
- Skalierbarkeit auf komplexere Szenarien (z. B. mehrere Bälle).
- Energieeffizienz der RL-Steuerung vs. klassischer Ansätze.

---

## 7. Zusammenfassung & Ausblick
### Fazit
- Was wurde erreicht? Welche Ziele wurden übertroffen/verfehlt?

### Zukünftige Arbeiten
- Integration von Machine Vision für dynamischere Ballverfolgung.
- Einsatz in industriellen Anwendungen (z. B. Stabilisierung von Lasten).

---

## Anhänge
- Quellcode (GitHub-Link).
- Schaltpläne der Plattform.
- Rohdaten der Experimente.
- Ethikvotum (falls Nutzerstudien durchgeführt wurden).

---

## Tipps für die Umsetzung
- **Visualisierungen:** Nutze Diagramme der Kinematik, RL-Abläufe und Screenshots der Simulation.
- **Code-Dokumentation:** Halte den Code modular (separate Module für Kinematik, RL, Sensorik).
- **Agiles Vorgehen:** Arbeite iterativ – erst die Basisplattform, dann Nunchuk, dann RL.
- **Praxisbezug:** Betone den Anwendungsnutzen (z. B. RL-gesteuerte Plattformen für autonome Systeme).

Mit dieser Struktur zeigst du sowohl technische Tiefe als auch einen klaren roten Faden – viel Erfolg! 🚀
