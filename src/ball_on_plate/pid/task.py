import argparse

import numpy as np

class RunBallOnPlatePID:

    def parse(self, parser=None):
        parser = argparse.ArgumentParser(
            parents=[parser] if parser else [],
            prog='Train ball on plate',
            description='A program to control a Stewart platform for various test modes and experiments.',
            epilog='For more information, refer to the documentation or contact the developer.',
        )
        parser.add_argument(
            '-i',
            '--iterations',
            help='Number of iterations to run the experiment.',
            required=False,
            type=int,
            default=10
        )
        parser.add_argument(
            '-fps',
            help='Frames per second for the simulation or data capture.',
            required=False,
            type=int,
            default=10
        )
        parser.add_argument(
            '--simulation_mode',
            help='Enable simulation mode without actual hardware.',
            required=False,
            action='store_true',
            default=False,
        )
        parser.add_argument(
            '--friction',
            help='Friction coefficient of the plate (0-1).',
            required=False,
            type=int,
            default=0.8
        )
        parser.add_argument(
            '--kp',
            help='Proportional gain for the PID controller.',
            required=False,
            type=int,
            default=1.0
        )
        parser.add_argument(
            '--ki',
            help='Integral gain for the PID controller.',
            required=False,
            type=int,
            default=0.0
        )
        parser.add_argument(
            '--kd',
            help='Derivative gain for the PID controller.',
            required=False,
            type=int,
            default=0.5
        )
        parser.add_argument(
            '--circle',
            help='Enable circular motion of the ball on the plate.',
            required=False,
            type=bool,
            default=False
        )
        parser.add_argument(
            '--radius',
            '-r',
            help='Radius of the circle in circular motion mode (meters).',
            required=False,
            type=float,
            default=0.05
        )
        parser.add_argument(
            '--steps',
            '-s',
            help='Number of steps to complete the circular motion.',
            required=False,
            type=int,
            default=80
        )

        args, _ = parser.parse_known_args()
        self.iterations = args.iterations
        self.simulation_mode = args.simulation_mode
        self.fps = args.fps
        self.friction = args.friction
        self.kp = args.kp
        self.ki = args.ki
        self.kd = args.kd
        self.circle = args.circle
        self.radius = args.radius
        self.steps = args.steps

    def manual(self, iterations, simulation_mode, fps, friction, kp, ki, kd, circle, radius, steps):
        self.iterations = iterations
        self.simulation_mode = simulation_mode
        self.fps = fps
        self.friction = friction
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.circle = circle
        self.radius = radius
        self.steps = steps

    def run(self, logger):
        from src.ball_on_plate.pid.v3.simulation.agent import BallOnPlate
        agent = BallOnPlate(fps=self.fps, simulation_mode=self.simulation_mode, friction=self.friction, Kp=self.kp, Ki=self.ki, Kd=self.kd)

        if self.circle:
            max_steps = self.steps
            __angles = np.linspace(0, 2 * np.pi, int(max_steps))
            radius = self.radius # m
            __steps = 0
            while(True):
                agent.target_pos = (
                    radius * np.cos(__angles[__steps]),
                    radius * np.sin(__angles[__steps])
                )
                __steps += 1
                if __steps >= max_steps:
                    __steps = 0

                finish, isOnTarget, boarder_crossed = agent.perform_action()
                print(f"Is on target: {isOnTarget}")
                agent.render()
        else:
            for _ in range(self.iterations):
                agent.reset()
                agent.render()
                while(True):
                    finish, isOnTarget, boarder_crossed = agent.perform_action()
                    print(f"Is on target: {isOnTarget}")
                    agent.render()
                    if finish:
                        print("Episode is Successful!")
                        break
                    elif boarder_crossed:
                        print("Episode Failed!")
                        break
