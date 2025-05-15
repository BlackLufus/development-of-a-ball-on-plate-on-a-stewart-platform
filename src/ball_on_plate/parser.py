import argparse

class TrainBallOnPlateParser:

    def parser(self, parser=None):
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

class RunBallOnPlateParser:

    def parser(self, parser=None):
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

        self.args, _ = parser.parse_known_args()

    def run(self, logger):
        from src.ball_on_plate.v0.training import run_sb3
        run_sb3(
            self.args.env,
            self.args.id,
            self.args.model_name,
            self.args.model,
            self.args.device,
            self.args.iterations,
            self.args.simulation_mode,
            self.args.fps,
            logger
        )
