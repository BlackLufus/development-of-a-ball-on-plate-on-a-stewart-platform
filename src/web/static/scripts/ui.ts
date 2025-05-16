import BallOnPlate from './window/content/ball_on_plate.js';
import VideoCam from './window/content/video_cam.js';
import Frame from './window/frame.js';

const darkModeSwitch = document.getElementById('dark-mode');
if (darkModeSwitch) {
    darkModeSwitch.addEventListener('change', function() {
        UI.updateDarkMode();
    });
}

const element1 = document.getElementById('element_1');
if (element1) {
    element1.addEventListener('click', () => {
        const frame = new Frame('Hallo', undefined, undefined);
        frame.show()
    });
}

const video_cam = document.getElementById('video_cam');
if (video_cam) {
    video_cam.addEventListener('click', () => {
        const live_cam = new VideoCam("localhost", 6500, "video_cam");
        live_cam.show();
    });
}

const ball_on_plate = document.getElementById('ball_on_plate');
if (ball_on_plate) {
    ball_on_plate.addEventListener('click', () => {
        const live_cam = new BallOnPlate("localhost", 6500, "run_ball_on_plate");
        live_cam.show();
    });
}

class UI {

    static init(): void {
    }

    // Function to update the dark mode
    static updateDarkMode(): void {
        if (darkModeSwitch && 'checked' in darkModeSwitch) {
            document.documentElement.setAttribute('data-theme', (darkModeSwitch as HTMLInputElement).checked ? 'dark' : 'light');
        }
    }
}

export default UI;