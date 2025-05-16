import argparse
import asyncio
from queue import Queue
import io
import threading
import time

import PIL

class TrainBallOnPlate:

    def parse(self, parser=None):
        parser = argparse.ArgumentParser(
            parents=[parser] if parser else [],
            prog='Train ball on plate',
            description='A program to control a Stewart platform for various test modes and experiments.',
            epilog='For more information, refer to the documentation or contact the developer.'
        )
        parser.add_argument(
            '-e',
            '--env',
            help='',
            required=False,
            type=str,
            choices=['BallOnPlate-v0'],
            default='BallOnPlate-v0'
        )
        parser.add_argument(
            '--dir',
            help='',
            required=True,
            type=str
        )
        parser.add_argument(
            '-m',
            '--model',
            help='',
            required=False,
            type=str,
            choices=['ppo', 'dqn', 'a2c'],
            default='ppo'
        )
        parser.add_argument(
            '--use_existing_model_dir',
            help='',
            required=False,
            type=str
        )
        parser.add_argument(
            '-d',
            '--device',
            help='',
            required=False,
            type=str,
            choices=['cpu', 'cuda', 'auto'],
            default='cpu'
        )
        parser.add_argument(
            '--sequential_execution',
            help='',
            required=False,
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '-i',
            '--iterations',
            help='',
            required=False,
            type=int,
            default=40
        )
        parser.add_argument(
            '-s',
            '--steps_per_iteration',
            help='',
            required=False,
            type=int,
            default=5_000
        )

        self.args, _ = parser.parse_known_args()

    def run(self, logger):
        from src.ball_on_plate.v0.training import train_sb3
        train_sb3(
            self.args.env, 
            self.args.dir, 
            self.args.model, 
            self.args.use_existing_model_dir, 
            self.args.device, 
            self.args.sequential_execution,
            self.args.iterations, 
            self.args.steps_per_iteration, 
            logger
        )

class RunBallOnPlate:

    def parse(self, parser=None):
        parser = argparse.ArgumentParser(
            parents=[parser] if parser else [],
            prog='Train ball on plate',
            description='A program to control a Stewart platform for various test modes and experiments.',
            epilog='For more information, refer to the documentation or contact the developer.',
        )
        parser.add_argument(
            '-e',
            '--env',
            help='',
            required=False,
            type=str,
            choices=['BallOnPlate-v0'],
            default='BallOnPlate-v0'
        )
        parser.add_argument(
            '--id',
            help='',
            required=True,
            type=str
        )
        parser.add_argument(
            '-n',
            '--model_name',
            help='',
            required=False,
            type=str,
            default="best_model.zip"
        )
        parser.add_argument(
            '-m',
            '--model',
            help='',
            required=False,
            type=str,
            choices=['ppo', 'dqn', 'a2c'],
            default='ppo'
        )
        parser.add_argument(
            '-d',
            '--device',
            help='',
            required=False,
            type=str,
            choices=['cpu', 'cuda', 'auto'],
            default='cpu'
        )
        parser.add_argument(
            '-i',
            '--iterations',
            help='',
            required=False,
            type=int,
            default=10
        )
        parser.add_argument(
            '--simulation_mode',
            help='',
            required=False,
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '--fps',
            help='',
            required=False,
            type=int,
            default=60
        )

        args, _ = parser.parse_known_args()
        self.env = args.env
        self.id = args.id
        self.model_name = args.model_name
        self.model = args.model
        self.device = args.device
        self.iterations = args.iterations
        self.simulation_mode = args.simulation_mode
        self.fps = args.fps

    def manual(self, env, id, model_name, model, device, iterations, simulation_mode, fps):
        self.env = env
        self.id = id
        self.model_name = model_name
        self.model = model
        self.device = device
        self.iterations = iterations
        self.simulation_mode = simulation_mode
        self.fps = fps

    def run(self, logger):
        from src.ball_on_plate.v0.training import run_sb3
        run_sb3(
            self.env,
            self.id,
            self.model_name,
            self.model,
            self.device,
            self.iterations,
            self.simulation_mode,
            self.fps,
            logger
        )

    async def run_async(self, logger, ws):
        from src.ball_on_plate.v0.training import run_sb3

        try:
            image_queue = asyncio.Queue()
            stop_event = asyncio.Event()
            loop = asyncio.get_running_loop()

            def raw_image_event(image_bytes):
                # Sende das Bild sicher in die Async-Queue
                asyncio.run_coroutine_threadsafe(image_queue.put(image_bytes), loop)
            
            # Funktion, die im Thread läuft
            def run_training():
                run_sb3(
                    self.env,
                    self.id,
                    self.model_name,
                    self.model,
                    self.device,
                    self.iterations,
                    self.simulation_mode,
                    self.fps,
                    logger,
                    raw_image_event
                )
                # Training ist vorbei – signalisiere das auch, falls nötig:
                asyncio.run_coroutine_threadsafe(stop_event.set(), loop)

            # Starte run_sb3 in separatem Thread
            threading.Thread(target=run_training, daemon=True).start()

            while not stop_event.is_set():
                try:
                    image = await asyncio.wait_for(image_queue.get(), timeout=1.0)
                    if image:
                        await ws.send(image)
                except asyncio.TimeoutError:
                    continue
        except:
            pass

