import StreamButton from "./stream_button.js";

class ImageStreamError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "ImageStreamError";
        Object.setPrototypeOf(this, ContextMenuError.prototype);
    }
}

class ImageStream extends StreamButton {

    public readonly element: HTMLElement;
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D | null;
    private death_screen: HTMLImageElement;

    constructor(width: number, height: number, start_event: () => void, stop_event: () => void) {
        super(start_event, stop_event);
        this.element = document.createElement('div');

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        this.element.appendChild(canvas);
        this.element.appendChild(this.stream_buttons);

        const ctx = canvas.getContext('2d');

        this.canvas = canvas;
        this.ctx = ctx;

        this.death_screen = document.createElement('img');
        this.death_screen.src = './static/assets/svg/stop_button.svg';
        this.death_screen.alt = 'Deathscreen';
    }

    drawFrame(image: HTMLImageElement) {
        this.ctx?.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx?.drawImage(image, 0, 0, this.canvas.width, this.canvas.height);
    }
}

export default ImageStream;