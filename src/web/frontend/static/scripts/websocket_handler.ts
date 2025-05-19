export enum TaskId {
    SET = 'set',
    CIRCLE = 'circle',
    NUNCHUCK = 'nunchuck',
    VIDEO_CAM = 'video_cam',
    BALL_ON_PLATE = 'ball_on_plate'
}

export enum State {
    CONNECT = 'connect',
    DISCONNECT = 'disconnect'
}

export class WebSocketHandlerListener {

    public id: number;
    public task_id: TaskId;
    public event: (success: boolean, payload: object) => void;

    constructor(id: number, task_id: TaskId, event: (success: boolean, payload: object) => void) {
        this.id = id;
        this.task_id = task_id;
        this.event = event;
    }
}

class WebSocketHandlerError extends Error {

    constructor(message: string) {
        super(message);
        this.name = "WebSocketHandlerError";
        Object.setPrototypeOf(this, WebSocketHandlerError.prototype);
    }
}

class WebSocketHandler {

    private static wsh?: WebSocketHandler;

    private url: string
    private websocket?: WebSocket;
    private switchElement?: HTMLInputElement;

    private listener: Array<WebSocketHandlerListener> = [];

    private constructor(url: string) {
        this.url = url;
    }

    public register(switchElement: HTMLInputElement): void {
        this.switchElement = switchElement;
    }

    public connect(): void {
        this.websocket = new WebSocket(`ws://${this.url}`);

        this.websocket.addEventListener('open', event => {
            if (this.switchElement) {
                this.switchElement.checked = true;
            }
            console.log("Connected");
        });

        this.websocket.addEventListener('message', event => {
            const message = JSON.parse(event.data);
            console.log(message);
            const {task_id, success, response} = message;
            for (let i = 0; i < this.listener.length; i++) {
                if (this.listener[i].task_id == task_id) {
                    this.listener[i].event(success, response);
                }
            }
        });

        this.websocket.addEventListener('error', event => {
            console.log(`Error: ${event}`);
        });

        this.websocket.addEventListener('close', event => {
            if (this.switchElement) {
                this.switchElement.checked = false;
            }
            console.log("Disconnected");
        });
    }

    public static send(task_id: TaskId, state: State, payload: object): boolean {
        if (this.wsh && this.wsh.websocket && this.wsh.websocket.readyState != WebSocket.CLOSED) {
            this.wsh.websocket.send(JSON.stringify({
                'task_id': task_id,
                'state': state,
                'payload': payload
            }));
            return true;
        }
        return false;
    }

    public static subscribe(id: number, task_id: TaskId, event: (success: boolean, payload: object) => void): void {
        if (!this.wsh) {
            throw new WebSocketHandlerError('There is no WebSocketHandler instance!');
        }
        else {
            this.wsh.listener.push(new WebSocketHandlerListener(id, task_id, event));
        }
    }

    public static unsubscribe(id: number) {
        if (this.wsh) {
            for (let i  = 0; i < this.wsh.listener.length; i++) {
                if (this.wsh.listener[i].id == id) {
                    this.wsh.listener.splice(i, 1);
                }
            }
        }
    }

    public disconnect(): void {
        if (this.websocket) {
            if (this.websocket.readyState == WebSocket.CLOSED) {
                throw new WebSocketHandlerError("Websocket is currently not connected!");
            }
            else {
                this.websocket.close();
            }
        }
        else {
            throw new WebSocketHandlerError("WebSocket is not initialized yet.");
        }
    }

    public static instance(url_path: string): WebSocketHandler {
        if (!this.wsh) {
            this.wsh = new WebSocketHandler(url_path);
        }
        return this.wsh;
    }


}

export default WebSocketHandler;