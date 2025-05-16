import Frame from "../frame.js";
import ImageStream from "./elements/image_stream.js";

class BallOnPlate extends Frame {
    address: string;
    port: number;
    api_end_point: string;
    socket?: WebSocket;
    image_stream?: ImageStream;
    
    /**
     * Creates a BallOnPlate frame
     * @param {string} address 
     * @param {number} port 
     * @param {string} api_end_point 
     */
    constructor(address: string, port: number, api_end_point: string) {
        const container = document.createElement('div');

        super("Ball On Plate", container, () => this.terminate());

        this.address = address;
        this.port = port;
        this.api_end_point = api_end_point;

        this.build(container);
        this.connect();
    }

    /**
     * Connects to an API enpoint
     * @returns {void}
     */
    private connect(): void {
        this.socket = new WebSocket(`ws://${this.address}:${this.port}/${this.api_end_point}`);

        // Connection opened
        this.socket.addEventListener("open", (event) => {
            console.log("Stream is open");
        });

        // Listen for messages
        this.socket.addEventListener("message", (event) => {
            if (this.image_stream != null) {
                const blob = event.data;

                const img = new Image();
                img.onload = () => {
                    this.image_stream?.drawFrame(img);
                }
                img.src = URL.createObjectURL(blob);
            }
        });

        this.socket.addEventListener("close", (event) => {
            this.dispose();
        });

        this.socket.addEventListener("error", (event) => {
            console.log(`Socket Errer: ${event}`);
            this.dispose();
        });
    }

    private build(container: HTMLElement): void {
        this.image_stream = new ImageStream(512, 632);
        container.appendChild(this.image_stream.canvas);
    }

    private terminate = () => {
        if (this.socket) {
            console.log("Connection closed");
            this.socket.close();
            this.socket = undefined;
        }
    }
}

export default BallOnPlate;