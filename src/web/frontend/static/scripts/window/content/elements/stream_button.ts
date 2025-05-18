class StreamButton {

    protected readonly stream_buttons: HTMLElement;
    private play_button: HTMLImageElement;
    private stop_button: HTMLImageElement;

    constructor(start_event: () => void, stop_event: () => void) {
        this.stream_buttons = document.createElement('div');
        this.stream_buttons.className = 'stream_button';

        this.play_button = document.createElement('img');
        this.play_button.className = 'stream_button_element';
        this.play_button.src = './static/assets/svg/play_button.svg';
        this.play_button.alt = 'Play Button';
        this.play_button.addEventListener(
            'click',
            () => {
                start_event();
                this.start();
            }
        )

        this.stop_button = document.createElement('img');
        this.stop_button.className = 'stream_button_element';
        this.stop_button.src = './static/assets/svg/stop_button.svg';
        this.stop_button.alt = 'Stop Button';
        this.stop_button.addEventListener(
            'click',
            () => {
                stop_event();
                this.stop();
            }
        )

        this.stop();
    }

    public start(): void {
        if (this.stream_buttons.contains(this.play_button)) {
            this.stream_buttons.removeChild(this.play_button);
        }
        this.stream_buttons.appendChild(this.stop_button);
    }

    public stop(): void {
        if (this.stream_buttons.contains(this.stop_button)) {
            this.stream_buttons.removeChild(this.stop_button);
        }
        this.stream_buttons.appendChild(this.play_button);
    }
}

export default StreamButton;