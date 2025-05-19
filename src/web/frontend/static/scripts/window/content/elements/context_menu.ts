class ContextMenuError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "ContextMenuError";
        Object.setPrototypeOf(this, ContextMenuError.prototype);
    }
}


class ContextMenu {
    
}