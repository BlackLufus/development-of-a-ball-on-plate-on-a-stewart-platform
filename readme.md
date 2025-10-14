# Development of a ball-on-plate prototype on a Stewart platform with comparison between PID and reinforcement learning

## 📌 Project description

This project deals with the **development of a ball-on-plate prototype** on a **Stewart platform**.  
The goal is to stabilize and control the ball precisely on a moving plate—both with a **classical PID controller** and with a **reinforcement learning agent (RL)**.  
By comparing these two approaches, the strengths and weaknesses of model-based and learning-based control systems will be investigated.

## 🛠️ General conditions

The implementation of this project is based entirely on existing components:

- Stewart platform with 6 actuators
- Six EMAX-ES09MD servo motors
- Logitech Brio for ball position determination
- Nvidia Jetson TX2 Development Kit for controlling servo motors via the I2C interface

### 💻 System requirements

- **Betriebssystem** Ubuntu 18.04
- **Python** 3.12.10  
- **Node.js** v20.17.0
- **NPM Version** 10.8.2
- **tsc Version** 5.8.3

### 📦 Required Python packages

The required dependencies can be installed via `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 🪄 Compiling TypeScript to JavaScript

The web front end of the project is based on **TypeScript** and must be converted to **JavaScript** before execution.

### 1. Install dependencies
Navigate to the `web/frontend` directory and install the required npm packages:

```bash
cd src/web/frontend
npm install
```

### 2. Compiling TypeScript

Compilation is performed using the tsconfig.json file included in the project.
To do this, execute the following command in the main directory or in the frontend folder:

```bash
npx tsc
```

## 📂 Project structure

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

## 🧩 Additional modules

```nunchuck/``` – Nunchuck control for manual platform control

```video_capture/``` – Direct camera access

```stewart_platform/``` – Low-level servo control, kinematics, PCA9685 control

```parser_manager.py``` – Configuration management via **config.json**

## 🚀 Application

Some functions can be executed directly via main:

```bash
python -m src.main --help
```

### Control the Stewart platform directly

```bash
python -m src.main --run set
```

or

```bash
python -m src.main --run circle
```

### Nunchuck control

```bash
python -m src.main --run nunchuck
```

### Video capture

```bash
python -m src.main --run video_capture_linux
```

### Run simulation (RL or PID)

```bash
python -m src.main --run ball_on_plate
```

### Execute/train simulation (RL or PID)

```bash
python -m src.ball_on_plate.rl.v3.simulation.train
```

or

```bash
python -m src.ball_on_plate.pid.v2.simulation.agent
```

### Perform/train physically (RL or PID)

```bash
python -m src.ball_on_plate.rl.v3.physical.train
```

or

```bash
python -m src.ball_on_plate.pid.v2.physical.agent
```

### Web interface

```bash
python -m src.web.manage runserver 127.0.0.1:8000
```

## 🧾 Lizenz

This project is licensed under the `MIT` License.\\
For details, see LICENSE.