import WebSocketHandler, { State, TaskId } from "../../websocket_handler.js";
import Frame from "../frame.js";
import ImageStream from "./elements/image_stream.js";
import MenuBar, { MenuBarItem } from "./elements/menu_bar.js";

enum MenuBarTask {
    VIRTUAL = 'virtual',
    STREAM = 'stream'
}

/**
 * BallOnPlateError is a custom error class for handling errors specific to the Ball On Plate simulation.
 * It extends the built-in Error class and sets the name property to "BallOnPlateError".
 */
class BallOnPlatePhysicalError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "BallOnPlateError";
        Object.setPrototypeOf(this, BallOnPlatePhysicalError.prototype);
    }
}

/**
 * Represents the Ball On Plate frame, providing a singleton interface for managing
 * the visualization and communication with the Ball On Plate simulation backend.
 * 
 * This class handles the connection to the backend via WebSocket, manages the image
 * stream for displaying simulation frames, and provides lifecycle management for the frame.
 */
class BallOnPlatePhysical extends Frame {

    private static instance?: BallOnPlatePhysical;
    image_stream?: ImageStream;
    private selected_task: MenuBarTask = MenuBarTask.VIRTUAL;
    private readonly content_elememt: HTMLElement = document.createElement('div');
    
    /**
     * Creates a BallOnPlate frame.
     * @private
     * @remarks
     * Use the static {@link BallOnPlatePhysical.get} method to obtain the singleton instance.
     */
    private constructor() {
        const container = document.createElement('div');

        super("Ball On Plate Physical", container, () => this.terminate());

        this.build(container);
    }

    /**
     * Retrieves the singleton instance of the BallOnPlate frame.
     * @returns {BallOnPlate} The singleton instance.
     */
    public static get(): BallOnPlatePhysical {
        if (!this.instance) {
            this.instance = new BallOnPlatePhysical();
        }
        return this.instance;
    }

    /**
     * Connects to an API enpoint
     * @returns {void}
     */
    private connect(): void {
        WebSocketHandler.subscribe(this.id, TaskId.BALL_ON_PLATE_PHYSICAL, (state: boolean, payload: any) => {
            if (this.image_stream) {
                if (state) {
                    try {
                        if (payload) {
                            const frame = payload[this.selected_task];
                            // response is expected to be a base64 string
                            const img = new Image();
                            img.onload = () => {
                                this.image_stream?.drawFrame(img);
                            };
                            img.src = `data:image/jpeg;base64,${frame}`;
                        }
                    } catch (e) {
                        throw new BallOnPlatePhysicalError("Failed to parse message or draw frame: " + e);
                    }
                }
                else {
                    this.image_stream?.stop();
                }
            }
        });
    }

    /**
     * Sends a connection payload to the backend.
     * @private
     */
    private send(): void {
        WebSocketHandler.send(
            TaskId.BALL_ON_PLATE_PHYSICAL,
            State.CONNECT,
            {
                'env': 'BallOnPlate-v0',
                'id': '0_9',
                'model_name': 'best_model.zip',
                'sb3_model': 'ppo',
                'device': 'cpu',
                'iterations': 10,
                'simulation_mode': false,
                'fps': 10
            }
        );
    }

    /**
     * Disconnects from the Ball On Plate simulation backend and unsubscribes from updates.
     * @private
     */
    private disconnect(): void {
        WebSocketHandler.send(
            TaskId.BALL_ON_PLATE_PHYSICAL, 
            State.DISCONNECT, 
            {}
        );
        WebSocketHandler.unsubscribe(this.id);
    }

    /**
     * Builds the Ball On Plate frame UI by initializing the image stream and appending it to the container.
     * @param container - The HTML container element for the frame.
     * @private
     */
    private build(container: HTMLElement): void {
        container.classList.add('control_panel');
        const menu_bar = new MenuBar(
            [
                new MenuBarItem('virtual', 'Physical'),
                new MenuBarItem('stream', 'Stream'),
            ],
            this.task_changed,
            1
        );
        container.appendChild(menu_bar.element);
        this.setContent();
        container.appendChild(this.content_elememt);
    }

    /**
     * Handles the task change event and updates the selected task.
     * Disconnects from the previous task and sets the new task.
     * 
     * @param {MenuBarTask} task_id - The ID of the selected task.
     * @private
     */
    private task_changed = (task_id: MenuBarTask) => {
        this.selected_task = task_id;
        this.setContent();
    }

    /**
     * Sets the content of the Control Panel based on the selected task.
     * 
     * @private
     */
    private setContent(): void {
        console.log(this.selected_task);
        this.content_elememt.innerHTML = "";
        switch(this.selected_task) {
            case MenuBarTask.VIRTUAL:
                this.image_stream = new ImageStream(512, 632, this.start, this.stop);
                this.content_elememt.style.maxHeight = "632px";
                this.content_elememt.appendChild(this.image_stream.element);
                break;
            case MenuBarTask.STREAM:
                this.image_stream = new ImageStream(1024, 576, this.start, this.stop);
                this.content_elememt.style.maxHeight = "576px";
                this.content_elememt.appendChild(this.image_stream.element);
                break;
        }
    }

    /**
     * Starts the Ball On Plate simulation by establishing the backend connection.
     * @private
     */
    private start = (): void => {
        console.log("BallOnPlate: Start");
        this.connect();
        this.send();
    }

    /**
     * Stops the Ball On Plate simulation by disconnecting from the backend.
     * @private
     */
    private stop = (): void => {
        console.log("BallOnPlate: Stop");
        this.disconnect();
    }

    /**
     * Terminates the Ball On Plate frame, performing cleanup and resetting the singleton instance.
     * @private
     */
    private terminate = () => {
        this.stop();
        console.log("BallOnPlate: Terminate Node");
        BallOnPlatePhysical.instance = undefined;
    }
}

export default BallOnPlatePhysical;