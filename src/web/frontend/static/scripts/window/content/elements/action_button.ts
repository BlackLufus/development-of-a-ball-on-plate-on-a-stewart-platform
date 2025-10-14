class ActionButtonError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "ActionButtonError";
        Object.setPrototypeOf(this, ActionButtonError.prototype);
    }
}


class ActionButton {
    
    public readonly element: HTMLElement;

    constructor(name: string, clickEvent: () => void) {
        this.element = document.createElement('button');
        this.build(name, clickEvent);
    }

    private build(name: string, clickEvent: () => void): void {
        this.element.addEventListener(
            'click',
            clickEvent
        );
        const action_button_span = document.createElement('span');
        action_button_span.innerText = name;
        this.element.appendChild(action_button_span);
    }
}

export default ActionButton