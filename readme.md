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
├── models/
│   └── bop
│       ├── ...
│       └── 4_0
├── node_modules/
├── recorded_images/
├── src/
│   ├── ball_on_plate/
│   │   ├── pid/
│   │   │   ├── ...
│   │   │   ├── v3/
│   │   │   │   ├── physical/
│   │   │   │   │   ├── images/
│   │   │   │   │   └── agent.py
│   │   │   │   ├── simulation/
│   │   │   │   │   ├── images/
│   │   │   │   │   └── agent.py
│   │   │   │   └── pid_simulate_ball_on_plate_v3.ipynb
│   │   │   └── task.py
│   │   ├── rl/
│   │   │   ├── ...
│   │   │   ├── v4/
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
│   │   │   └── task.py
│   │   └── README.md
│   ├── detection/
│   │   ├── opencv/
│   │   │   ├── images/
│   │   │   ├── ball_tracker copy.py
│   │   │   ├── ball_tracker_approach_1.ipynb
│   │   │   ├── ball_tracker_approach_2.ipynb
│   │   │   └── ball_tracker.py
│   │   └── yolo/
│   │       ├── ac_detection.py
│   │       ├── cv_detection.py
│   │       └── train_yolo_with_ball_on_plate.ipynb
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
│   ├── vacuum_robot/
│   │   ├── analyse/
│   │   ├── images/
│   │   ├── v0/
│   │   ├── ...
│   │   ├── v3/
│   │   │   ├── agent.py
│   │   │   ├── environment.py
│   │   │   └── training.py
│   │   └── q_table.py
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
│   ├── parser_manager.py
│   ├── tensorboard/
│   │   ├── ...
│   │   └── bop
│   │       ├── ...
│   │       └── 4_0
│   └── venv/
├── requirements.txt
├── tsconfig.json
└── README.md
```

## 🧩 Additional modules

```nunchuck/``` – Nunchuck control for manual platform control

```video_capture/``` – Direct camera access

```stewart_platform/``` – Low-level servo control, kinematics, PCA9685 control

```parser_manager.py``` – Configuration management via **config.json**

## 🎥 Checking Connected Cameras

Before using the recorder, you can verify which camera is connected and what settings are available.

### 1. List all connected video devices

```bash
v4l2-ctl --list-devices
```

This command shows all cameras detected by your system along with their device paths (e.g., `/dev/video0`, `/dev/video1`).

### 2. Check supported formats and options for a specific device

```bash
v4l2-ctl --device=/dev/video1 --list-formats-ext
```

Replace `/dev/video1` with the device path of your camera. This will display all supported resolutions, frame rates, and pixel formats.

> ⚠️ Note: `v4l2-ctl`is typically available on Linux systems. Windows users will need to use their system’s camera settings or other tools.

## 📊 Viewing Logs with TensorBoard

You can monitor training progress, metrics, and visualizations using TensorBoard.

### 1. Start TensorBoard

```bash
tensorboard --logdir ./tensorboard/
```

This command starts a local TensorBoard server using the logs stored in `./tensorboard/`.

### 2. Open in a browser

After starting, TensorBoard will provide a local URL (e.g., `http://localhost:6006`). Open this in your browser to explore your training metrics, graphs, and summaries.

> ⚠️ Make sure TensorBoard is installed in your Python environment. You can install it with:
> ```bash
> pip install tensorboard
> ```

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
python -m src.ball_on_plate.rl.v4.simulation.train
```

or

```bash
python -m src.ball_on_plate.pid.v3.simulation.agent
```

### Perform/train physically (RL or PID)

```bash
python -m src.ball_on_plate.rl.v4.physical.train
```

or

```bash
python -m src.ball_on_plate.pid.v3.physical.agent
```

### Image recorder

```bash
python -m src.main --run image_recorder -f 15 -t 200 --os 'linux'
```

### Web interface

```bash
python -m src.web.manage runserver 127.0.0.1:8000
```

## Download models

> [rl_model_4_0](https://drive.google.com/file/d/1qXxIWzX0APrrYirxvvCHgpOYDEqDvQCG/view?usp=drive_link)

## 🧾 Lizenz

This project is licensed under the `MIT` License.\\
For details, see LICENSE.
