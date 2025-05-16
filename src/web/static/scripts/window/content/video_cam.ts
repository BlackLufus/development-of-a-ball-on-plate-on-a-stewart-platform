import Frame from "../frame.js";
import ImageStream from "./elements/image_stream.js";

class VideoCam extends Frame {
    private address: string;
    private port: number;
    private api_end_point: string;
    private socket?: WebSocket;
    private image_stream?: ImageStream;
    
    /**
     * Creates a VideoCam frame
     * @param {string} address 
     * @param {number} port 
     * @param {string} api_end_point 
     */
    constructor(address: string, port: number, api_end_point: string) {
        const container = document.createElement('div');

        super("Live Cam", container, () => this.terminate());

        this.address = address;
        this.port = port;
        this.api_end_point = api_end_point;

        this.build(container)
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

    /**
     * Builds content
     * @param {HTMLDivElement} container 
     * @returns {void}
     */
    private build(container: HTMLDivElement): void {
        this.image_stream = new ImageStream(600, 400);
        container.appendChild(this.image_stream.canvas);
    }

    /**
     * A function to terminate all connections
     * @returns {void}
     */
    private terminate = () => {
        if (this.socket) {
            console.log("Connection closed");
            this.socket.close();
            this.socket = undefined;
        }
    }
}

export default VideoCam;