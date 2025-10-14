import argparse

class ImageRecorder:

    def parse(self, parser=None):
        parser = argparse.ArgumentParser(
            parents=[parser] if parser else [],
            prog='Image Recorder',
            description='Capture images from the Stewart platform over a specified duration.',
            epilog='For more information, refer to the documentation or contact the developer.'
        )
        parser.add_argument(
            '-f',
            '--fps',
            help='Frames per second to capture.',
            required=False,
            type=int,
            default=15
        )
        parser.add_argument(
            '-t',
            '--total_frames',
            help='Total number of frames to capture.',
            required=False,
            type=int,
            default=400
        )
        parser.add_argument(
            '--os',
            help='Operating system to use for the recorder.',
            required=False,
            type=str,
            choices=['linux', 'windows'],
            default='linux'
        )

        args, _ = parser.parse_known_args()
        self.fps = args.fps
        self.total_frames = args.total_frames
        self.os = args.os

    def manual(self, fps, total_frames, os):
        self.fps = fps
        self.total_frames = total_frames
        self.os = os

    def run(self, logger):
        from src.video_capture.recorder.image_recorder import ImageRecorder
        ImageRecorder(self.fps, self.total_frames, self.os)
