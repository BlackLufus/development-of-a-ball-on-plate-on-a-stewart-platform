import WebSocketHandler, { State, TaskId } from "../../websocket_handler.js";
import Frame from "../frame.js";
import MenuBar, { MenuBarItem } from "./elements/menu_bar.js";

class ControlPanel extends Frame {

    private static instance?: ControlPanel;
    private selected_task: TaskId = TaskId.SET;

    private constructor() {
        const container = document.createElement('div');

        super("Control panel", container, () => this.terminate());

        this.build(container);
    }

    public static get(): ControlPanel {
        if (!this.instance) {
            this.instance = new ControlPanel();
        }
        return this.instance;
    }

    /**
     * Connects to an API enpoint
     * @returns {void}
     */
    private connect(task_id:TaskId): void {
        WebSocketHandler.subscribe(this.id, task_id, (state: boolean, payload: object) => {
            if (true) {
                if (state) {
                    try {
                        if (payload) {

                        }
                    } catch (e) {
                        console.error("Failed to parse message or draw frame:", e);
                    }
                }
            }
        });

        WebSocketHandler.send(
            task_id,
            State.CONNECT,
            {
                
            }
        );
    }

    private disconnect(task_id: TaskId): void {
        WebSocketHandler.send(
            task_id, 
            State.DISCONNECT, 
            {}
        );
        WebSocketHandler.unsubscribe(this.id);
    }

    private build(container: HTMLElement): void {
        container.classList = 'control_panel';
        const menu_bar = new MenuBar(
            [
                new MenuBarItem(TaskId.SET, 'Set'),
                new MenuBarItem(TaskId.CIRCLE, 'Circle'),
                new MenuBarItem(TaskId.NUNCHUCK, 'Nunchuck')
            ],
            this.task_changed
        );
        container.appendChild(menu_bar.element);
    }

    private start = (): void => {
        console.log("ControlPanel: Start");
        this.connect(this.selected_task);
    }

    private stop = (): void => {
        console.log("ControlPanel: Stop");
        this.disconnect(this.selected_task);
    }

    private task_changed = (taskId: TaskId) => {
        this.stop();
        this.selected_task = taskId;
        this.start();
    }

    private terminate = () => {
        this.stop();
        console.log("ControlPanel: Terminate Node");
        ControlPanel.instance = undefined;
    }
}

export default ControlPanel;