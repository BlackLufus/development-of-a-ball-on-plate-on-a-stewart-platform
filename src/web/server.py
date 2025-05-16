from queue import SimpleQueue
import threading
import cv2
from flask import Flask, send_from_directory
import asyncio
from websockets.server import serve
from urllib.parse import urlparse

app = Flask(__name__, static_folder="static", static_url_path="/")

@app.route("/")
def index(path=None):
    if not path or path == "/" or path == "index.html":
        return send_from_directory("static", "index.html")
    else:
        return send_from_directory("static", path)
    
def start_flask():
    app.run(port=6750)

async def run_ball_on_plate_handler(websocket):
    from src.ball_on_plate.task import RunBallOnPlate
    print("Client connected...")
    model = RunBallOnPlate()
    model.manual('BallOnPlate-v0', '0_9', 'best_model.zip', 'ppo', 'cpu', 10, False, 60)
    await model.run_async(None, websocket)
    print("Client disconnected...")

async def video_cam_handler(websocket):
    from src.video_capture.task import VideoCaptureWindows
    print("Client connected...")
    model = VideoCaptureWindows()
    model.manual("Logitech BRIO", "1280x720", 30)
    await model.run_async(None, websocket)
    print("Client disconnected...")

async def main_route(websocket, path: str):
    print(path)
    if path == "/video_cam":
        await video_cam_handler(websocket)
    elif path == "/run_ball_on_plate":
        await run_ball_on_plate_handler(websocket)
    else:
        await websocket.close()
        
async def main():
    async with serve(main_route, "localhost", 6500) as server:
        await server.serve_forever()

if __name__ == '__main__':
    # Start the API Server
    # api.run(host="0.0.0.0", port=7750)
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    asyncio.run(main())