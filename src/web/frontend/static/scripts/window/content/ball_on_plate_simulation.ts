import WebSocketHandler, { State, TaskId } from "../../websocket_handler.js";
import Frame from "../frame.js";
import ImageStream from "./elements/image_stream.js";

/**
 * BallOnPlateError is a custom error class for handling errors specific to the Ball On Plate simulation.
 * It extends the built-in Error class and sets the name property to "BallOnPlateError".
 */
class BallOnPlateSimulationError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "BallOnPlateError";
        Object.setPrototypeOf(this, BallOnPlateSimulationError.prototype);
    }
}

/**
 * Represents the Ball On Plate frame, providing a singleton interface for managing
 * the visualization and communication with the Ball On Plate simulation backend.
 * 
 * This class handles the connection to the backend via WebSocket, manages the image
 * stream for displaying simulation frames, and provides lifecycle management for the frame.
 */
class BallOnPlateSimulation extends Frame {

    private static instance?: BallOnPlateSimulation;
    image_stream?: ImageStream;
    
    /**
     * Creates a BallOnPlate frame.
     * @private
     * @remarks
     * Use the static {@link BallOnPlate.get} method to obtain the singleton instance.
     */
    private constructor() {
        const container = document.createElement('div');

        super("Ball On Plate Simulation", container, () => this.terminate());

        this.build(container);
    }

    /**
     * Retrieves the singleton instance of the BallOnPlate frame.
     * @returns {BallOnPlate} The singleton instance.
     */
    public static get(): BallOnPlateSimulation {
        if (!this.instance) {
            this.instance = new BallOnPlateSimulation();
        }
        return this.instance;
    }

    /**
     * Connects to an API enpoint
     * @returns {void}
     */
    private connect(): void {
        WebSocketHandler.subscribe(this.id, TaskId.BALL_ON_PLATE, (state: boolean, payload: object) => {
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
                        throw new BallOnPlateSimulationError("Failed to parse message or draw frame: " + e);
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
            TaskId.BALL_ON_PLATE,
            State.CONNECT,
            {
                'env': 'BallOnPlate-v4',
                'id': '4_0',
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
            TaskId.BALL_ON_PLATE, 
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
        this.image_stream = new ImageStream(512, 632, this.start, this.stop);
        container.style.maxHeight = "632px";
        container.appendChild(this.image_stream.element);
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
        BallOnPlateSimulation.instance = undefined;
    }
}

export default BallOnPlateSimulation;