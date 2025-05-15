import argparse
import logging

import cv2


class VideoCaptureParserLinux:
    """
    A class to handle Video Capture on Linux.
    """
    def parser(self, parser=None):
        parser = argparse.ArgumentParser(
            parents=[parser] if parser else [],
            prog='Set',
            usage='%(prog)s [options]',
            description='Start the video capture.',
            epilog='Example: %(prog)s -d /dev/video1 -r 1280x720 -f 20',
        )
        parser.add_argument(
            '-d',
            '--device_name',
            help='Set the device name',
            required=False,
            type=str,
            default='/dev/video0'
        )
        parser.add_argument(
            '-r',
            '--resolution',
            help='Set the resolution',
            required=False,
            type=str,
            default='1280x720'
        )
        parser.add_argument(
            '-f',
            '--framerate',
            help='Set the framerate',
            required=False,
            type=int,
            default=20
        )

        self.args, _ = parser.parse_known_args()

    def run(self, logger):        
        from src.video_capture.video_capture import CameraThreadWithAV

        logger = logger or logging.getLogger(__name__)

        # Initialize the video capture
        cam = CameraThreadWithAV(
            device_name=self.args.device_name,
            options={
                "video_size": self.args.resolution,
                "framerate": str(self.args.framerate),
                "input_format": "mjpeg"
            },
            format="v4l2",
            logger=logger
        )

        last_frame_num = cam.frame_num
        try:
            while cam.running:
                if last_frame_num != cam.frame_num:
                    last_frame_num = cam.frame_num

                    frame, fps, frame_num = cam.read()
                    if frame is not None:
                        logger.debug(f"FPS: {fps} (num: {frame_num})")

                        # Anzeige des Bildes
                        cv2.imshow("Threaded Camera", frame)

                        # Mit 'q' beenden
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

        finally:
            cam.stop()

class VideoCaptureParserWindows:
    """
    A class to handle Video Capture on Windows.
    """
    def parser(self, parser=None):
        parser = argparse.ArgumentParser(
            parents=[parser] if parser else [],
            prog='Set',
            usage='%(prog)s [options]',
            description='Start the video capture.',
            epilog='Example: %(prog)s -d "Logitech BRIO" -r 1280x720 -f 20',
        )
        parser.add_argument(
            '-d',
            '--device_name',
            help='Set the device name',
            required=False,
            type=str,
            default='Logitech BRIO'
        )
        parser.add_argument(
            '-r',
            '--resolution',
            help='Set the resolution',
            required=False,
            type=str,
            default='1280x720'
        )
        parser.add_argument(
            '-f',
            '--framerate',
            help='Set the framerate',
            required=False,
            type=int,
            default=20
        )

        self.args, _ = parser.parse_known_args()

    def run(self, logger):        
        from src.video_capture.video_capture import CameraThreadWithAV

        logger = logger or logging.getLogger(__name__)

        # Initialize the video capture
        cam = CameraThreadWithAV(
            device_name=f"video={self.args.device_name}",
            options={
                "video_size": self.args.resolution,
                "framerate": str(self.args.framerate),
                "input_format": "mjpeg"
            },
            format="dshow",
            logger=logger
        )

        last_frame_num = cam.frame_num
        try:
            while cam.running:
                if last_frame_num != cam.frame_num:
                    last_frame_num = cam.frame_num

                    frame, fps, frame_num = cam.read()
                    if frame is not None:
                        logger.debug(f"FPS: {fps} (num: {frame_num})")

                        # Anzeige des Bildes
                        cv2.imshow("Threaded Camera", frame)

                        # Mit 'q' beenden
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

        finally:
            cam.stop()
