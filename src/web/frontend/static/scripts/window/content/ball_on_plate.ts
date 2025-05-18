import WebSocketHandler, { State, TASK_ID } from "../../websocket_handler.js";
import Frame from "../frame.js";
import ImageStream from "./elements/image_stream.js";

class BallOnPlate extends Frame {

    private static instance?: BallOnPlate;
    image_stream?: ImageStream;
    
    /**
     * Creates a BallOnPlate frame
     * @param {string} address 
     * @param {number} port 
     * @param {string} api_end_point 
     */
    private constructor() {
        const container = document.createElement('div');

        super("Ball On Plate", container, () => this.terminate());

        this.build(container);
    }

    public static get(): BallOnPlate {
        if (!this.instance) {
            this.instance = new BallOnPlate();
        }
        return this.instance;
    }

    /**
     * Connects to an API enpoint
     * @returns {void}
     */
    private connect(): void {
        WebSocketHandler.subscribe(this.id, TASK_ID.BALL_ON_PLATE, (state: boolean, payload: object) => {
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
            TASK_ID.BALL_ON_PLATE,
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

    private disconnect(): void {
        WebSocketHandler.send(
            TASK_ID.BALL_ON_PLATE, 
            State.DISCONNECT, 
            {}
        );
    }

    private build(container: HTMLElement): void {
        this.image_stream = new ImageStream(512, 632, this.start, this.stop);
        container.style.maxHeight = "632px";
        container.appendChild(this.image_stream.element);
    }

    private start = (): void => {
        console.log("BallOnPlate: Start");
        this.connect();
    }

    private stop = (): void => {
        console.log("BallOnPlate: Stop");
        this.disconnect();
    }

    private terminate = () => {
        this.stop();
        console.log("BallOnPlate: Terminate Node");
        BallOnPlate.instance = undefined;
    }
}

export default BallOnPlate;