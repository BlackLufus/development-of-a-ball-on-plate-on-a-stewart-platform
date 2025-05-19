class Input {

    public readonly element: HTMLElement;
    constructor(name: string) {
        this.element = document.createElement('div');

        this.build();
    }

    private build(): void {
        this.element.classList = 'input_element';
    }
}