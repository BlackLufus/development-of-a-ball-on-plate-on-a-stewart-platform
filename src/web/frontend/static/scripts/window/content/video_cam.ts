import WebSocketHandler, { State, TASK_ID } from "../../websocket_handler.js";
import Frame from "../frame.js";
import ImageStream from "./elements/image_stream.js";

class VideoCam extends Frame {

    private image_stream?: ImageStream;
    
    /**
     * Creates a VideoCam frame
     * @param {string} address 
     * @param {number} port 
     * @param {string} api_end_point 
     */
    constructor() {
        const container = document.createElement('div');

        super("Live Cam", container, () => this.terminate());

        this.build(container)
        this.connect();
    }

    /**
     * Connects to an API enpoint
     * @returns {void}
     */
    private connect(): void {
        
        WebSocketHandler.subscribe(this.id, TASK_ID.VIDEO_CAM, (state: boolean, payload: object) => {
            if (this.image_stream && state) {
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
        });

        WebSocketHandler.send(
            TASK_ID.VIDEO_CAM,
            State.CONNECT,
            {
                'resolution': '1280x720',
                'fps': 30
            }
        );
    }

    /**
     * Builds content
     * @param {HTMLDivElement} container 
     * @returns {void}
     */
    private build(container: HTMLDivElement): void {
        this.image_stream = new ImageStream(600, 400);
        container.style.maxHeight = "400px";
        container.appendChild(this.image_stream.canvas);
    }

    /**
     * A function to terminate all connections
     * @returns {void}
     */
    private terminate = () => {
        WebSocketHandler.send(TASK_ID.VIDEO_CAM, State.DISCONNECT, {});
        console.log("Connection closed");
    }
}

export default VideoCam;