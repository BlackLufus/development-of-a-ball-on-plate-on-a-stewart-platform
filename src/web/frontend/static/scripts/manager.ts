import BallOnPlate from './window/content/ball_on_plate.js';
import VideoCam from './window/content/video_cam.js';
import Frame from './window/frame.js';
import WebSocketHandler from './websocket_handler.js';
import ControlPanel from './window/content/control_panel.js';

class Manager {

    private static instance: Manager;

    private constructor () {
        this.registerDarkMode();
        this.registerWebsocket();
        this.registerControlPanel();
        this.registerVideoCam();
        this.registerBallOnPlate();
    }

    public static get(): Manager {
        if (!this.instance) {
            this.instance = new Manager();
        }
        return this.instance;
    }

    // Function to update the dark mode
    private registerDarkMode(): void {
        const darkModeSwitch = document.getElementById('dark-mode');
        if (darkModeSwitch) {
            darkModeSwitch.addEventListener('change', () => {
                document.documentElement.setAttribute('data-theme', (darkModeSwitch as HTMLInputElement).checked ? 'dark' : 'light');
            });
        }
    }

    private registerWebsocket(): void {
        const websocketSwitch = document.getElementById('websocket');
        const websocket_li = document.getElementById('websocket_li');
        if (websocketSwitch && websocket_li) {
            const wsh = WebSocketHandler.instance(`${window.location.host}/ws`);
            wsh.register(websocketSwitch as HTMLInputElement);
            websocket_li.addEventListener('click', (event) => {
                event.preventDefault();
                let checked = (websocketSwitch as HTMLInputElement).checked;
                checked ? wsh.disconnect() : wsh.connect();
            });
        }
    }

    private registerControlPanel(): void {
        const element1 = document.getElementById('control_panel');
        if (element1) {
            element1.addEventListener('click', () => {
                const frame = ControlPanel.get();
                frame.show()
            });
        }
    }

    private registerVideoCam(): void {
        const video_cam = document.getElementById('video_cam');
        if (video_cam) {
            video_cam.addEventListener('click', () => {
                const live_cam = VideoCam.get();
                live_cam.show();
            });
        }
    }

    private registerBallOnPlate(): void {
        const ball_on_plate = document.getElementById('ball_on_plate');
        if (ball_on_plate) {
            ball_on_plate.addEventListener('click', () => {
                const live_cam = BallOnPlate.get();
                live_cam.show();
            });
        }
    }
}

export default Manager;