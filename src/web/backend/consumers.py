import asyncio
import base64
import json
from queue import Queue
import threading
import time
from channels.generic.websocket import AsyncWebsocketConsumer
import cv2

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        await self.send(json.dumps({"status": "CONNECTED"})) 

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("Received:", data)
        await self.send(json.dumps({"response": "ACK"}))
    
class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket verbunden")

    async def disconnect(self, close_code):
        print("WebSocket getrennt")

    async def receive(self, text_data):
        print("Empfangen:", text_data)
        await self.send(text_data=text_data)

class StewartPlatformConsumer(AsyncWebsocketConsumer):

    is_connected = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._set_thread = None

        self._circle_thread = None
        self._circle_stop_event = threading.Event()

        self._nunchuck_thread = None
        self._nunchuck_stop_event = threading.Event()

        self._video_cam_thread = None
        self._video_cam_stop_event = threading.Event()

        self._run_ball_on_plate_thread = None
        self._run_ball_on_plate_stop_event = threading.Event()

        with open('./src/config.json', 'r') as f:
            config_data = json.load(f)
            self.base_radius = config_data['settings']['base_radius']
            self.base_angle = config_data['settings']['base_angle']
            self.platform_radius = config_data['settings']['platform_radius']
            self.platform_angle = config_data['settings']['platform_angle']

    async def connect(self):
        if self.is_connected:
            await self.disconnect()
        else:
            print("Client connected...")
            await self.accept()
            self.send("Hallo")
    
    async def receive(self, text_data=None, bytes_data=None):
        print(text_data)
        json_data = json.loads(text_data)

        task_id = json_data.get('task_id')
        state = json_data.get('state')
        payload = json_data.get('payload', {})
        print(task_id)

        match task_id:
            case 'set':
                if state == 'connect':
                    if self._set_thread and self._set_thread.is_alive():
                        await self.send_response(task_id, False, 'Already connected to set task!')
                    else:
                        x = payload.get('x')
                        y = payload.get('y')
                        z = payload.get('z')
                        roll = payload.get('roll')
                        pitch = payload.get('pitch')
                        yaw = payload.get('yaw')
                        await self.run_set_handler(x, y, z, roll, pitch, yaw)
                elif state == 'disconnect':
                    print("disconnect fronm set task") 
                    await self.stop_set_handler()
            case 'circle':
                if state == 'connect':
                    if self._circle_thread and self._circle_thread.is_alive():
                        await self.send_response(task_id, False, 'Already connected to circle task!')
                    else:
                        radius = payload.get('radius')
                        steps = payload.get('steps')
                        period = payload.get('period')
                        smooth = payload.get('smooth')
                        await self.run_circle_handler(radius, steps, period, smooth)
                elif state == 'disconnect':
                    print("disconnect from circle task") 
                    await self.stop_circle_handler()
            case 'nunchuck':
                if state == 'connect':
                    if self._nunchuck_thread and self._nunchuck_thread.is_alive():
                        await self.send_response(task_id, False, 'Already connected to nunchuck task!')
                    else:
                        radius = payload.get('radius')
                        period = payload.get('period')
                        use_accelerometer = payload.get('use_accelerometer')
                        await self.run_nunchuck_handler(radius, period, use_accelerometer)
                elif state == 'disconnect':
                    print("disconnect from nunchuck task") 
                    await self.stop_nunchuck_handler()
            case 'video_cam':
                if state == 'connect':
                    if self._video_cam_thread and self._video_cam_thread.is_alive():
                        await self.send_response(task_id, False, 'Already connected to video cam!')
                    else:
                        platform = payload.get('platform')
                        device_name = payload.get('device_name')
                        resolution = payload.get('resolution')
                        fps = payload.get('fps')
                        await self.run_video_cam_handler(platform, device_name, resolution, fps)
                elif state == 'disconnect':
                    print("disconnect") 
                    await self.stop_video_cam_handler()
            case 'ball_on_plate':
                if state == 'connect':
                    if self._run_ball_on_plate_thread and self._run_ball_on_plate_thread.is_alive():
                        await self.send_response(task_id, False, 'Already connected to ball on plate!')
                    else:
                        env = payload.get('env')
                        id = payload.get('id')
                        model_name = payload.get('model_name')
                        sb3_model = payload.get('sb3_model')
                        device = payload.get('device')
                        iterations = payload.get('iterations')
                        simulation_mode = payload.get('simulation_mode')
                        fps = payload.get('fps')
                        await self.run_ball_on_plate_handler(env, id, model_name, sb3_model, device, iterations, simulation_mode, fps)
                elif state == 'disconnect':
                    print("disconnect") 
                    await self.stop_ball_on_plate_handler()
            case _:
                await self.send_response(task_id, False, 'Task does not match with any existing tasks!')

    async def disconnect(self, code):
        print("Client disconnected...")
        # Stop video cam thread if running
        await self.stop_set_handler()
        await self.stop_circle_handler()
        await self.stop_nunchuck_handler()
        await self.stop_video_cam_handler()
        await self.stop_ball_on_plate_handler()

    async def stop_set_handler(self):
        if self._set_thread and self._set_thread.is_alive():
            self._set_thread.join(timeout=2)

    async def run_set_handler(self, x, y, z, roll, pitch, yaw):
        loop = asyncio.get_running_loop()

        def start_ball_on_plate(loop):
            from src.stewart_platform.task import Set

            try:
                model = Set(self.base_radius, self.base_angle, self.platform_radius, self.platform_angle)
                model.manual(
                    x,
                    y,
                    z,
                    roll,
                    pitch,
                    yaw
                )
                model.run(
                    None
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(e)
                asyncio.run_coroutine_threadsafe(
                    self.send_response('set', False, e),
                    loop
                )
            finally:
                asyncio.run_coroutine_threadsafe(
                    self.send_response('set', False, 'Set task ended'),
                    loop
                )

        # Starte Thread
        self._set_thread = threading.Thread(target=start_ball_on_plate, args=(loop,), daemon=True)
        self._set_thread.start()

    
    # Circle Section
    async def stop_circle_handler(self):
        if self._circle_thread and self._circle_thread.is_alive():
            self._circle_stop_event.set()
            self._circle_thread.join(timeout=2)

    async def run_circle_handler(self, radius, steps, period, smooth):
        self._circle_stop_event.clear()
        loop = asyncio.get_running_loop()

        def run(loop):
                
            from src.stewart_platform.task import Circle
            try:
                model = Circle(self.base_radius, self.base_angle, self.platform_radius, self.platform_angle)
                model.manual(radius, steps, period, smooth)
                model.run(
                    None,
                    self._circle_stop_event
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(e)
                asyncio.run_coroutine_threadsafe(
                    self.send_response('circle', False, e),
                    loop
                )

        # Starte Thread
        self._circle_thread = threading.Thread(target=run, args=(loop,), daemon=True)
        self._circle_thread.start()


    # Nunchuck Section
    async def stop_nunchuck_handler(self):
        if self._nunchuck_thread and self._nunchuck_thread.is_alive():
            self._nunchuck_stop_event.set()
            self._nunchuck_thread.join(timeout=2)

    async def run_nunchuck_handler(self, radius, period, use_accelerometer):
        self._nunchuck_stop_event.clear()
        loop = asyncio.get_running_loop()

        def run(loop):
                
            from src.nunchuk.task import Nunchuk
            try:
                model = Nunchuk(self.base_radius, self.base_angle, self.platform_radius, self.platform_angle)
                model.manual(radius, period, use_accelerometer)
                model.run(
                    None,
                    self._nunchuck_stop_event
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(e)
                asyncio.run_coroutine_threadsafe(
                    self.send_response('circle', False, e),
                    loop
                )

        # Starte Thread
        self._nunchuck_thread = threading.Thread(target=run, args=(loop,), daemon=True)
        self._nunchuck_thread.start()


    # Ball on Plate Section
    async def stop_ball_on_plate_handler(self):
        if self._run_ball_on_plate_thread and self._run_ball_on_plate_thread.is_alive():
            self._run_ball_on_plate_stop_event.set()
            self._run_ball_on_plate_thread.join(timeout=2)

    async def run_ball_on_plate_handler(self, env, id, model_name, sb3_model, device, iterations, simulation_mode, fps):
        self._run_ball_on_plate_stop_event.clear()
        loop = asyncio.get_running_loop()

        def start_ball_on_plate(loop):
            from src.ball_on_plate.rl.task import RunBallOnPlateRL

            def raw_image_event(buffer):
                if not self._run_ball_on_plate_stop_event.is_set():
                    b64_image = base64.b64encode(buffer).decode('utf-8')

                    # Sende die base64-Daten an den Client (über asyncio)
                    asyncio.run_coroutine_threadsafe(
                        self.send_response('ball_on_plate', True, b64_image),
                        loop
                    )
            try:
                model = RunBallOnPlateRL()
                model.manual(
                    env,
                    id,
                    model_name,
                    sb3_model,
                    device,
                    iterations,
                    simulation_mode,
                    fps
                )
                model.run(
                    None,
                    raw_image_event,
                    self._run_ball_on_plate_stop_event
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(e)
                asyncio.run_coroutine_threadsafe(
                    self.send_response('ball_on_plate', False, e),
                    loop
                )
            finally:
                asyncio.run_coroutine_threadsafe(
                    self.send_response('ball_on_plate', False, 'Ball on plate ended'),
                    loop
                )

        # Starte Thread
        self._run_ball_on_plate_thread = threading.Thread(target=start_ball_on_plate, args=(loop,), daemon=True)
        self._run_ball_on_plate_thread.start()


    # Video Cam Section
    async def stop_video_cam_handler(self):
        if self._video_cam_thread and self._video_cam_thread.is_alive():
            self._video_cam_stop_event.set()
            self._video_cam_thread.join(timeout=2)

    async def run_video_cam_handler(self, platform, device_name, resolution, fps):
        self._video_cam_stop_event.clear()
        loop = asyncio.get_running_loop()

        def run(loop):

            def raw_image_event(frame):
                if not self._video_cam_stop_event.is_set():
                    _, buffer = cv2.imencode('.jpg', frame)
                    b64_image = base64.b64encode(buffer).decode('utf-8')

                    # Sende die base64-Daten an den Client (über asyncio)
                    asyncio.run_coroutine_threadsafe(
                        self.send_response('video_cam', True, b64_image),
                        loop
                    )
            if platform == 'linux':
                from src.video_capture.task import VideoCaptureLinux
            else:
                from src.video_capture.task import VideoCaptureWindows
            try:
                if platform == 'linux':
                    model = VideoCaptureLinux()
                else:
                    model = VideoCaptureWindows()
                model.manual(device_name, resolution, fps)
                model.run(
                    None,
                    raw_image_event,
                    self._video_cam_stop_event
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(e)
                asyncio.run_coroutine_threadsafe(
                    self.send_response('video_cam', False, e),
                    loop
                )

        # Starte Thread
        self._video_cam_thread = threading.Thread(target=run, args=(loop,), daemon=True)
        self._video_cam_thread.start()


    async def send_response(self, task_id: str, success: bool, response):
        await self.send(text_data=json.dumps({
            'task_id': task_id,
            'success': success,
            'response': str(response)
        }))