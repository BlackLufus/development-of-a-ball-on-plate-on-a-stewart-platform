import asyncio
import base64
import json
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
        self._video_cam_thread = None
        self._video_cam_stop_event = threading.Event()

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
            case 'video_cam':
                if state == 'connect':
                    print("connect")
                    if self._video_cam_thread and self._video_cam_thread.is_alive():
                        await self.send_response(task_id, False, 'Already connected to video cam!')
                    else:
                        resolution = payload.get('resolution')
                        fps = payload.get('fps')
                        await self.video_cam_handler(resolution, fps)
                elif state == 'disconnect':
                    print("disconnect") 
                    await self.stop_video_cam_handler()
            case 'ball_on_plate':
                pass
            case _:
                await self.send_response(task_id, False, 'Task does not match with any existing tasks!')

    async def disconnect(self, code):
        print("Client disconnected...")
        # Stop video cam thread if running
        await self.stop_video_cam_handler()

    async def stop_video_cam_handler(self):
        if self._video_cam_thread and self._video_cam_thread.is_alive():
            self._video_cam_stop_event.set()
            self._video_cam_thread.join(timeout=2)

    async def video_cam_handler(self, resolution, fps):
        self._video_cam_stop_event.clear()
        loop = asyncio.get_running_loop()

        def start_cam(loop):
            from src.video_capture.video_capture import CameraThreadWithAV
            try:
                cam = CameraThreadWithAV(
                    device_name=f"video=Logitech BRIO",
                    options={
                        "video_size": resolution,
                        "framerate": str(fps),
                        "input_format": "mjpeg"
                    },
                    format="dshow",
                    logger=None
                )
                last_frame_num = cam.frame_num
                try:
                    while cam.running and not self._video_cam_stop_event.is_set():
                        frame, _, _ = cam.read()
                        if last_frame_num != cam.frame_num:
                            last_frame_num = cam.frame_num

                            # Encode frame to base64
                            _, buffer = cv2.imencode('.jpg', frame)
                            b64_image = base64.b64encode(buffer).decode('utf-8')

                            # Sende die base64-Daten an den Client (über asyncio)
                            asyncio.run_coroutine_threadsafe(
                                self.send_response('video_cam', True, b64_image),
                                loop
                            )

                        # kurze Pause, um CPU nicht zu überlasten
                        time.sleep(0.01)  
                
                except Exception as e:
                    print(e)
                finally:
                    cam.stop()
                    asyncio.run_coroutine_threadsafe(
                        self.send_response('video_cam', False, 'Video stream ended'),
                        loop
                    )
            except Exception as e:
                asyncio.run_coroutine_threadsafe(
                    self.send_response('video_cam', False, e),
                    loop
                )

        # Starte Thread
        self._video_cam_thread = threading.Thread(target=start_cam, args=(loop,), daemon=True)
        self._video_cam_thread.start()


    async def send_response(self, task_id: str, success: bool, response):
        await self.send(text_data=json.dumps({
            'task_id': task_id,
            'success': success,
            'response': str(response)
        }))