# Development of a Ball-on-Plate Prototype on a Stewart Platform

## 📌 Projektbeschreibung

Dieses Projekt beschäftigt sich mit der **Entwicklung eines Ball-on-Plate-Prototyps** auf einer **Stewart-Plattform**.  
Das Ziel ist es, den Ball präzise auf einer beweglichen Platte zu stabilisieren und zu steuern — sowohl mit einem **klassischen PID-Regler** als auch mit einem **Reinforcement-Learning-Agenten (RL)**.  
Durch den Vergleich dieser beiden Ansätze sollen die Stärken und Schwächen von modellbasierten und lernbasierten Regelungen untersucht werden.

## 🛠️ Rahmenbedingungen

Die Umsetzung diese Projekts baut vollständig auf bereits vorhandenen Komponenten auf:

- Stewart-Plattform mit 6 Aktuatoren
- Sechs EMAX-ES09MD-Servomotoren
- Logitech Brio zur Ballpositionsbestimmung
- Nvidia Jetson TX2 Development Kit zum ansprechen von Servomotoren über die I2C Schnittstelle

### 💻 Systemanforderungen

- **Betriebssystem** Ubuntu 18.04
- **Python** 3.12.10  
- **Node.js** v20.17.0
- **NPM Version** 10.8.2
- **tsc Version** 5.8.3

### 📦 Erforderliche Python-Pakete

Die benötigten Abhängigkeiten können über `requirements.txt` installiert werden:

```bash
pip install -r requirements.txt
```

## 🪄 TypeScript zu JavaScript kompilieren

Das Web-Frontend des Projekts basiert auf **TypeScript** und muss vor der Ausführung in **JavaScript** transpiliert werden.

### 1. Abhängigkeiten installieren
Wechsle in das `web/frontend`-Verzeichnis und installiere die benötigten npm-Pakete:

```bash
cd src/web/frontend
npm install
```

### 2. TypeScript kompilieren

Die Kompilierung erfolgt mit dem im Projekt enthaltenen ```tsconfig.json```.
Führe dazu im Hauptverzeichnis oder im ```frontend```-Ordner folgenden Befehl aus:

```bash
npx tsc
```

## 📂 Projektstruktur

```bash
ball-on-plate/
├── src/
│   ├── ball_on_plate/
│   │   ├── pid/
│   │   │   ├── ...
│   │   │   ├── v2/
│   │   │   │   ├── physical/
│   │   │   │   │   ├── images/
│   │   │   │   │   └── agent.py
│   │   │   │   ├── simulation/
│   │   │   │   │   ├── images/
│   │   │   │   │   └── agent.py
│   │   ├── rl/
│   │   │   ├── ...
│   │   │   ├── v3/
│   │   │   │   ├── physical/
│   │   │   │   │   ├── images/
│   │   │   │   │   ├── agent.py
│   │   │   │   │   ├── environment.py
│   │   │   │   │   └── training.py
│   │   │   │   ├── simulation/
│   │   │   │   │   ├── images/
│   │   │   │   │   ├── agent.py
│   │   │   │   │   ├── environment.py
│   │   │   │   │   └── training.py
│   │   ├── task.py
│   ├── detection/
│   │   ├── opencv/
│   │   │   ├── ...
│   │   │   └── ball_tracker.py
│   │   ├── yolo/
│   │   │   ├── ac_detection.py
│   │   │   ├── cv_detection.py
│   │   │   └── recorder.py
│   ├── nunchuck/
│   │   ├── nunchuck.py
│   │   └── task.py
│   ├── stewart_plattform/
│   │   ├── PCA9685/
│   │   │   ├── PCA9685.py
│   │   ├── servo_motor_handler.py
│   │   ├── slider.py
│   │   ├── stewart_plattform.py
│   │   └── task.py
│   ├── video_capture/
│   │   ├── video_capture.py
│   │   └── task.py
│   ├── web/
│   │   ├── backend/
│   │   │   ├── consumer.py
│   │   │   └── ...
│   │   ├── frontend/
│   │   │   ├── assets/
│   │   │   ├── scripts/
│   │   │   ├── styles/
│   │   │   └── index.html
│   │   ├── server/
│   │   │   ├── asgi.py
│   │   │   ├── settings.py
│   │   │   ├── urls.py
│   │   │   └── wsgi.py
│   │   └── manager.py
│   ├── config.json
│   ├── main.py
│   └── parser_manager.py
├── requirements.txt
├── tsconfig.json
└── README.md
```

## 🧩 Weitere Module

```nunchuck/``` – Nunchuck-Steuerung zur manuellen Plattformkontrolle

```video_capture/``` – Direkter Kamera-Zugriff

```stewart_plattform/``` – Low-Level-Servosteuerung, Kinematik, PCA9685-Ansteuerung

```parser_manager.py``` – Konfigurationsverwaltung über **config.json**

## 🚀 Anwendung

Einige Funktionen können direkt über die main ausgeführt werden:

```bash
python -m src.main --help
```

### Stewart Plattform direkt steuern

```bash
python -m src.main --run set
```

oder 

```bash
python -m src.main --run circle
```

### Nunchuck Steuerung

```bash
python -m src.main --run nunchuck
```

### Video Abrage

```bash
python -m src.main --run video_capture_linux
```

### Simulation (RL oder PID) ausführen

```bash
python -m src.main --run ball_on_plate
```

### Simulation (RL oder PID) ausführen/trainieren

```bash
python -m src.ball_on_plate.rl.v3.simulation.train
```

oder

```bash
python -m src.ball_on_plate.pid.v2.simulation.agent
```

### Physisch (RL oder PID) ausführen/trainieren

```bash
python -m src.ball_on_plate.rl.v3.physical.train
```

oder

```bash
python -m src.ball_on_plate.pid.v2.physical.agent
```

### Weboberfläche

```bash
python -m src.web.manage runserver 127.0.0.1:8000
```

## 🧾 Lizenz

Dieses Projekt steht unter der ```MIT``` License.
Details siehe LICENSE.