import argparse
import json
import base64
import logging

import cv2


class VideoCaptureLinux():
    """
    A class to handle Video Capture on Linux.
    """
    def parse(self, parser=None):
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

        args, _ = parser.parse_known_args()
        self.device_name = args.device_name
        self.resolution = args.resolution
        self.framerate = args.framerate

    def manual(self, device_name, resolution, framerate):
        self.device_name = device_name
        self.resolution = resolution
        self.framerate = framerate

    def __build(self, logger):
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

        return logger, cam

    def run(self, logger, send_data = None):
        logger, cam = self.__build(logger)

        last_frame_num = cam.frame_num
        try:
            while cam.running:
                if last_frame_num != cam.frame_num:
                    last_frame_num = cam.frame_num

                    frame, fps, frame_num = cam.read()
                    if frame is not None:
                        logger.debug(f"FPS: {fps} (num: {frame_num})")

                        if send_data:
                            send_data(frame)
                        else:
                            # Anzeige des Bildes
                            cv2.imshow("Threaded Camera", frame)

                            # Mit 'q' beenden
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break

        finally:
            cam.stop()
    
    async def run_async(self, logger, ws):
        logger, cam = self.__build(logger)

        last_frame_num = cam.frame_num
        try:
            while cam.running:
                if last_frame_num != cam.frame_num:
                    last_frame_num = cam.frame_num

                    frame, fps, frame_num = cam.read()
                    if frame is not None:
                        logger.debug(f"FPS: {fps} (num: {frame_num})")

                        success, encoded_image = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                        if success:
                            await ws.send(encoded_image.tobytes())
        except Exception as e:
            logger.debug(e)
            pass
        finally:
            cam.stop()

class VideoCaptureWindows:
    """
    A class to handle Video Capture on Windows.
    """
    def parse(self, parser=None):
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

        args, _ = parser.parse_known_args()
        self.device_name = args.device_name
        self.resolution = args.resolution
        self.framerate = args.framerate

    def manual(self, device_name, resolution, framerate):
        self.device_name = device_name
        self.resolution = resolution
        self.framerate = framerate

    def __build(self, logger):
        from src.video_capture.video_capture import CameraThreadWithAV

        logger = logger or logging.getLogger(__name__)

        # Initialize the video capture
        cam = CameraThreadWithAV(
            device_name=f"video={self.device_name}",
            options={
                "video_size": self.resolution,
                "framerate": str(self.framerate),
                "input_format": "mjpeg"
            },
            format="dshow",
            logger=logger
        )

        return logger, cam

    def run(self):
        logger, cam = self.__build(logger)

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

    async def run_async(self, logger, send):
        logger, cam = self.__build(logger)

        last_frame_num = cam.frame_num
        try:
            while cam.running:
                if last_frame_num != cam.frame_num:
                    last_frame_num = cam.frame_num

                    frame, fps, frame_num = cam.read()
                    if frame is not None:
                        logger.debug(f"FPS: {fps} (num: {frame_num})")

                        success, encoded_image = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                        if success:
                            await send('video_cam', True, base64.b64encode(encoded_image.tobytes()))
                                # encoded_image.tobytes())
        except Exception as e:
            logger.debug(e)
            await send('video_cam', False, e)
            pass
        finally:
            cam.stop()

