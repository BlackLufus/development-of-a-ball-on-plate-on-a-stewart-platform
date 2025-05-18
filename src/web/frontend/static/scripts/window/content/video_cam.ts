import WebSocketHandler, { State, TASK_ID } from "../../websocket_handler.js";
import Frame from "../frame.js";
import ImageStream from "./elements/image_stream.js";

class VideoCam extends Frame {

    private static instance?: VideoCam;
    private image_stream?: ImageStream;
    
    /**
     * Creates a VideoCam frame
     * @param {string} address 
     * @param {number} port 
     * @param {string} api_end_point 
     */
    private constructor() {
        const container = document.createElement('div');

        super("Live Cam", container, () => this.terminate());

        this.build(container);
    }

    public static get(): VideoCam {
        if (!this.instance) {
            this.instance = new VideoCam();
        }
        return this.instance;
    }

    /**
     * Connects to an API enpoint
     * @returns {void}
     */
    private connect(): void {
        
        WebSocketHandler.subscribe(this.id, TASK_ID.VIDEO_CAM, (state: boolean, payload: object) => {
            if (this.image_stream) {
                if (state) {
                    try {
                        if (payload) {
                            // response is expected to be a base64 string
                            const img = new Image();
                            img.onload = () => {
                                this.image_stream?.drawFrame(img);
                            };
                            img.src = `data:image/jpeg;base64,${payload}`;
                        }
                    } catch (e) {
                        console.error("Failed to parse message or draw frame:", e);
                    }
                }
                else {
                    this.image_stream?.stop();
                }
            }
        });

        WebSocketHandler.send(
            TASK_ID.VIDEO_CAM,
            State.CONNECT,
            {
                'device_name': 'Logitech BRIO',
                'resolution': '1280x720',
                'fps': 30
            }
        );
    }

    private disconnect(): void {
        WebSocketHandler.send(TASK_ID.VIDEO_CAM, State.DISCONNECT, {});
    }

    /**
     * Builds content
     * @param {HTMLDivElement} container 
     * @returns {void}
     */
    private build(container: HTMLDivElement): void {
        this.image_stream = new ImageStream(600, 400, this.start, this.stop);
        container.style.maxHeight = "400px";
        container.appendChild(this.image_stream.element);
    }

    private start = (): void => {
        this.connect();
    }

    private stop = (): void => {
        this.disconnect();
    }

    /**
     * A function to terminate all connections
     * @returns {void}
     */
    private terminate = (): void => {
        this.stop();
        console.log("VideoCam: Terminate Node");
        VideoCam.instance = undefined;
    }
}

export default VideoCam;