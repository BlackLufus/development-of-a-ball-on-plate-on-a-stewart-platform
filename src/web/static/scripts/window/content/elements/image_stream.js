class ImageStream {

    constructor(width, height) {
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');

        this.canvas = canvas;
        this.ctx = ctx;
    }

    drawFrame(image) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(image, 0, 0, this.canvas.width, this.canvas.height);
    }
}

export default ImageStream;