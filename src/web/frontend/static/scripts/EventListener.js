class EventListener {

    // This is a static property that holds all the listeners
    static listeners = [];

    // This is a static method that adds an event listener to the element
    static addEventListener(element, type, callback, oneTimeEvent = false, id, options) {
        this.listeners.push(new EventListener(element, type, callback, oneTimeEvent, id, options));
    }

    // This is a static method that removes all the event listeners
    static removeAllListeners(id) {
        //const num = this.listeners.length;
        for (let i = 0; i < this.listeners.length; i++) {
            if (id === undefined || this.listeners[i].id === id) {
                this.listeners[i].removeListener();
                this.listeners.splice(i, 1);
                i--;
            }
        }
        //console.log(`Listeners removed: ${num - this.listeners.length} / ${num}`);
    }

    // This is the constructor for the EventListener class
    constructor(element, type, callback, oneTimeEvent = false, id, options) {
        this.element = element;
        this.type = type;
        this.callback = callback;
        this.oneTimeEvent = oneTimeEvent;
        this.id = id;
        this.options = options;
        
        // Bind the handleClick method to the instance of the class
        this.handleListenerEvent = this.handleListenerEvent.bind(this);

        this.addListener();
    }

    // This method is called when the event is triggered
    handleListenerEvent(e) {
        e.stopPropagation();
        this.callback(e);
        if (this.oneTimeEvent) {
            this.removeListener();
        }
    }

    // This method adds the event listener to the element
    addListener() {
        if (this.element === undefined || this.element === null) {
            throw new Error('element is required');
        }
        else if (this.callback === undefined || this.callback === null || typeof this.callback !== 'function') {
            throw new Error('callback is required');
        }
        else {
            if (this.options === null) {
                this.element.addEventListener(this.type, this.handleListenerEvent);
            }
            else {
                this.element.addEventListener(this.type, this.handleListenerEvent, this.options);
            }
        }
    }

    // This method removes the event listener from the element
    removeListener() {
        this.element.removeEventListener(this.type, this.handleListenerEvent);
    }
}

export default EventListener;