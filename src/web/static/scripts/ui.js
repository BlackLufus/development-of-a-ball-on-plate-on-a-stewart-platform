import BallOnPlate from './window/content/ball_on_plate.js';
import LiveCam from './window/content/live_cam.js';
import Frame from './window/frame.js';

const darkModeSwitch = document.getElementById('dark-mode');
darkModeSwitch.addEventListener('change', function() {
    UI.updateDarkMode();
});

const element1 = document.getElementById('element_1');
element1.addEventListener('click', () => {
    const frame = new Frame('Hallo', "null", null);
    frame.show()
});

const video_cam = document.getElementById('video_cam');
video_cam.addEventListener('click', () => {
    const live_cam = new LiveCam("localhost", 6500, "video_cam");
    live_cam.frame.show();
});

const ball_on_plate = document.getElementById('ball_on_plate');
ball_on_plate.addEventListener('click', () => {
    const live_cam = new BallOnPlate("localhost", 6500, "run_ball_on_plate");
    live_cam.frame.show();
});

class UI {

    static init() {
    }

    // Function to update the dark mode
    static updateDarkMode() {
        document.documentElement.setAttribute('data-theme', darkModeSwitch.checked ? 'dark' : 'light');
    }
}

export default UI;