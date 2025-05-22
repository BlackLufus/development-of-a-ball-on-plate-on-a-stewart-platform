import WebSocketHandler, { State, TaskId } from "../../websocket_handler.js";
import Frame from "../frame.js";
import ImageStream from "./elements/image_stream.js";

/**
 * BallOnPlateError is a custom error class for handling errors specific to the Ball On Plate simulation.
 * It extends the built-in Error class and sets the name property to "BallOnPlateError".
 */
class VideoCamError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "VideoCamError";
        Object.setPrototypeOf(this, VideoCamError.prototype);
    }
}

/**
 * Represents the Video Cam frame, providing a singleton interface for managing
 * the visualization and communication with the Video Cam simulation backend.
 * 
 * This class handles the connection to the backend via WebSocket, manages the image
 * stream for displaying simulation frames, and provides lifecycle management for the frame.
 */
class VideoCam extends Frame {

    private static instance?: VideoCam;
    private image_stream?: ImageStream;

    /**
     * Represents the Video Cam frame, providing a singleton interface for managing
     * the visualization and communication with the Video Cam simulation backend.
     * 
     * This class handles the connection to the backend via WebSocket, manages the input fields
     * for different tasks, and provides lifecycle management for the frame.
     */
    private constructor() {
        const container = document.createElement('div');

        super("Video Cam", container, () => this.terminate());

        this.build(container);
    }

    /**
     * Retrieves the singleton instance of the VideoCam frame.
     * @returns {VideoCam} The singleton instance.
     */
    public static get(): VideoCam {
        if (!this.instance) {
            this.instance = new VideoCam();
        }
        return this.instance;
    }

    /**
     * Connects to an API endpoint and subscribes to the video stream.
     * Handles incoming messages and updates the image stream accordingly.
     * @returns {void}
     * @throws {VideoCamError} If there is an error parsing the message or drawing the frame.
     * */    
    private connect(): void {
        
        WebSocketHandler.subscribe(this.id, TaskId.VIDEO_CAM, (state: boolean, payload: object) => {
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
                        throw new VideoCamError("Failed to parse message or draw frame: " + e);
                    }
                }
                else {
                    this.image_stream?.stop();
                }
            }
        });

        WebSocketHandler.send(
            TaskId.VIDEO_CAM,
            State.CONNECT,
            // Example for Windows
            // {
            //     'platform': 'windows',
            //     'device_name': 'Logitech BRIO',
            //     'resolution': '1280x720',
            //     'fps': 30
            // }
            // Example for Linux
            {
                'platform': 'linux',
                'device_name': '/dev/video0',
                'resolution': '1280x720',
                'fps': 10
            }
        );
    }

    /**
     * Sends a disconnect payload to the backend.
     * @returns {void}
     */
    private disconnect(): void {
        WebSocketHandler.send(TaskId.VIDEO_CAM, State.DISCONNECT, {});
        WebSocketHandler.unsubscribe(this.id);
    }

    /**
     * Builds the Video Cam frame by creating the image stream element and appending it to the container.
     * @param {HTMLDivElement} container - The container element for the frame.
     * @returns {void}
     */
    private build(container: HTMLDivElement): void {
        this.image_stream = new ImageStream(1024, 576, this.start, this.stop);
        container.style.maxHeight = "576px";
        container.appendChild(this.image_stream.element);
    }

    /**
     * Starts the Video Cam frame by connecting to the backend and subscribing to updates.
     * @returns {void}
     */
    private start = (): void => {
        this.connect();
    }

    /**
     * Stops the Video Cam frame by disconnecting from the backend and unsubscribing from updates.
     * @returns {void}
     */
    private stop = (): void => {
        this.disconnect();
    }

    /**
     * Terminates the Video Cam frame by stopping the image stream and unsubscribing from the WebSocket.
     * @returns {void}
     */
    private terminate = (): void => {
        this.stop();
        console.log("VideoCam: Terminate Node");
        VideoCam.instance = undefined;
    }
}

export default VideoCam;