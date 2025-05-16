import Frame from "../frame.js";
import ImageStream from "./elements/image_stream.js";

class BallOnPlate {
    
    constructor(address, port, api_end_point) {
        this.address = address;
        this.port = port;
        this.api_end_point = api_end_point;
        this.__connect();
        this.__build();
    }

    __connect() {
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
                    this.image_stream.drawFrame(img);
                }
                img.src = URL.createObjectURL(blob);
            }
        });

        this.socket.addEventListener("close", (event) => {
            this.frame.dispose();
        });

        this.socket.addEventListener("error", (event) => {
            console.log(`Socket Errer: ${event}`);
            this.frame.dispose();
        });
    }

    __build() {
        const container = document.createElement('div');
        this.frame = new Frame("Live Cam", container, this.terminate);

        this.image_stream = new ImageStream(512, 632);
        container.appendChild(this.image_stream.canvas);
    }

    terminate = () => {
        if (this.socket) {
            console.log("Connection closed");
            this.socket.close();
            this.socket = null;
        }
    }
}

export default BallOnPlate;