import WebSocketHandler, { State, TaskId } from "../../websocket_handler.js";
import Frame from "../frame.js";
import ActionButton from "./elements/action_button.js";
import { DropdownItem } from "./elements/dropdown.js";
import Input, { InputType } from "./elements/input.js";
import MenuBar, { MenuBarItem } from "./elements/menu_bar.js";

/**
 * ControlPanelError is a custom error class for handling errors specific to the Control Panel.
 * It extends the built-in Error class and sets the name property to "ControlPanelError".
 */
class ControlPanelError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "ControlPanelError";
        Object.setPrototypeOf(this, ControlPanelError.prototype);
    }
}

/**
 * Represents the Control Panel frame, providing a singleton interface for managing
 * the control panel and communication with the backend.
 * 
 * This class handles the connection to the backend via WebSocket, manages the input fields
 * for different tasks, and provides lifecycle management for the frame.
 */
class ControlPanel extends Frame {

    private static instance?: ControlPanel;
    private selected_task: TaskId = TaskId.SET;
    private values: Record<string, any> = {
        x: {
            type: InputType.NUMBER,
            value: 0,
            step: 0.1,
            min: -5,
            max: 5
        },
        y: {
            type: InputType.NUMBER,
            value: 0,
            step: 0.1,
            min: -5,
            max: 5
        },
        z: {
            type: InputType.NUMBER,
            value: 0,
            step: 0.1,
            min: -5,
            max: 5
        },
        roll: {
            type: InputType.NUMBER,
            value: 0,
            step: 0.1,
            min: -5,
            max: 5
        },
        pitch: {
            type: InputType.NUMBER,
            value: 0,
            step: 0.1,
            min: -5,
            max: 5
        },
        yaw: {
            type: InputType.NUMBER,
            value: 0,
            step: 0.1,
            min: -5,
            max: 5
        },
        radius: {
            type: InputType.NUMBER,
            value: 5.8,
            step: 0.1,
            min: -5,
            max: 5
        },
        steps: {
            type: InputType.NUMBER,
            value: 0.1,
            step: 0.005,
            min: 0.01,
            max: 5
        },
        period: {
            type: InputType.NUMBER,
            value: 0,
            step: 0.1,
            min: 0,
            max: 5
        },
        smooth: {
            type: InputType.DROPDOWN,
            value: true,
            index: 0,
            list: [
                new DropdownItem(true, "True"),
                new DropdownItem(false, "False")
            ]
        },
        use_accelerometer: {
            type: InputType.DROPDOWN,
            value: true,
            index: 0,
            list: [
                new DropdownItem(true, "True"),
                new DropdownItem(false, "False")
            ]
        }
    };
    private content_elememt: HTMLElement = document.createElement('div');

    /**
     * Private constructor to enforce singleton pattern.
     * Initializes the Control Panel frame and sets up the UI elements.
     * 
     * @private
     */
    private constructor() {
        const container = document.createElement('div');

        super("Control panel", container, () => this.terminate());

        this.build(container);
    }

    /**
     * Retrieves the singleton instance of the ControlPanel frame.
     * If the instance does not exist, it creates a new one.
     * 
     * @returns {ControlPanel} The singleton instance of the ControlPanel.
     */
    public static get(): ControlPanel {
        if (!this.instance) {
            this.instance = new ControlPanel();
        }
        return this.instance;
    }

    /**
     * Connects to the backend via WebSocket and subscribes to task updates.
     * Subscribes to the selected task and handles incoming messages.
     * 
     * @private
     */
    private connect(): void {
        WebSocketHandler.subscribe(this.id, this.selected_task, (state: boolean, payload: object) => {
            if (true) {
                if (state) {
                    try {
                        if (payload) {

                        }
                    } catch (e) {
                        throw new ControlPanelError("Failed to parse message or draw frame: " + e);
                    }
                }
            }
        });
    }

    /**
     * Sends the current task and its parameters to the backend.
     * 
     * @private
     */
    private send(): void {
        WebSocketHandler.send(
            this.selected_task,
            State.CONNECT,
            this.getPayloadForTask(this.selected_task)
        );
    }

    /**
     * Retrieves the payload for the specified task ID.
     * 
     * @param {TaskId} taskId - The ID of the task.
     * @returns {object} The payload object containing the task parameters.
     */
    private getPayloadForTask(taskId: TaskId): object {
        switch (taskId) {
            case TaskId.SET:
                return {
                    x: this.values.x.value,
                    y: this.values.y.value,
                    z: this.values.z.value,
                    roll: this.values.roll.value,
                    pitch: this.values.pitch.value,
                    yaw: this.values.yaw.value,
                };
            case TaskId.CIRCLE:
                return {
                    radius: this.values.radius.value,
                    steps: this.values.steps.value,
                    period: this.values.period.value,
                    smooth: this.values.smooth.value,
                };
            case TaskId.NUNCHUCK:
                return {
                    radius: this.values.radius.value,
                    period: this.values.period.value,
                    use_accelerometer: this.values.use_accelerometer.value,
                };
            default:
                return {};
        }
    }

    /**
     * Disconnects from the backend and unsubscribes from task updates.
     * 
     * @private
     */
    private disconnect(): void {
        WebSocketHandler.send(
            this.selected_task, 
            State.DISCONNECT, 
            {}
        );
        WebSocketHandler.unsubscribe(this.id);
    }

    /**
     * Builds the UI elements for the Control Panel frame.
     * 
     * @param {HTMLElement} container - The container element for the Control Panel.
     * @private
     */
    private build(container: HTMLElement): void {
        container.innerHTML = "";
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
        this.setContent();
        container.appendChild(this.content_elememt!);
    }

    /**
     * Sets the content of the Control Panel based on the selected task.
     * 
     * @private
     */
    private setContent(): void {
        console.log(this.selected_task);
        switch(this.selected_task) {
            case TaskId.SET:
                this.buildContent(
                    'Set Task',
                    'Task description',
                    'Agrumente',
                    [
                        new Input('x', 'X', this.values),
                        new Input('y', 'Y', this.values),
                        new Input('z', 'Z', this.values),
                        new Input('roll','Roll', this.values),
                        new Input('pitch', 'Pitch', this.values),
                        new Input('yaw', 'Yaw', this.values)
                    ],
                    'Aktionen',
                    [
                        new ActionButton('Übernehmen', () => this.connect())
                    ]
                );
                break;
            case TaskId.CIRCLE:
                this.buildContent(
                    'Circle Task',
                    'Task description',
                    'Agrumente',
                    [
                        new Input('radius', 'Radius', this.values),
                        new Input('steps', 'Steps', this.values),
                        new Input('period', 'Period', this.values),
                        new Input('smooth','Smooth', this.values)
                    ],
                    'Aktionen',
                    [
                        new ActionButton('Übernehmen', () => this.connect())
                    ]
                );
                break;
            case TaskId.NUNCHUCK:
                this.buildContent(
                    'Nunchuck Task',
                    'Task description',
                    'Agrumente',
                    [
                        new Input('radius', 'Radius', this.values),
                        new Input('period', 'Period', this.values),
                        new Input('use_accelerometer','Accelerometer', this.values)
                    ],
                    'Aktionen',
                    [
                        new ActionButton('Übernehmen', () => this.connect())
                    ]
                );
                break;
        }
    }

    /**
     * Builds the content of the Control Panel frame.
     * 
     * @param {string} task_name - The name of the task.
     * @param {string} task_description - The description of the task.
     * @param {string} argument_header_name - The header name for arguments.
     * @param {Array<Input>} agrument_list - The list of input elements for arguments.
     * @param {string} action_header_name - The header name for actions.
     * @param {Array<ActionButton>} actions_list - The list of action buttons.
     * @private
     */
    private buildContent(task_name: string, task_description: string, argument_header_name: string, agrument_list: Array<Input>, action_header_name: string, actions_list: Array<ActionButton>): void {
        this.content_elememt.innerHTML = "";
        
        const top_div = document.createElement('div');
        top_div.className = 'control_panel_setting_header';
        this.content_elememt.appendChild(top_div);

        const header = document.createElement('h1');
        header.innerText = task_name;
        top_div.appendChild(header);

        const description = document.createElement('span');
        description.innerText = task_description;
        top_div.appendChild(description);

        const content_div = document.createElement('div');
        content_div.className = 'control_panel_setting_options';
        this.content_elememt.appendChild(content_div);

        const argument_header = document.createElement('h2');
        argument_header.innerText = argument_header_name;
        content_div.appendChild(argument_header);

        agrument_list.forEach(agrument => {
            content_div.appendChild(agrument.element);
        });

        const actions_div = document.createElement('div');
        actions_div.className = 'control_panel_setting_actions';
        this.content_elememt.appendChild(actions_div);

        const action_header = document.createElement('h2');
        action_header.innerText = action_header_name;
        actions_div.appendChild(action_header);

        actions_list.forEach(action => {
            actions_div.appendChild(action.element);
        });
    }

    /**
     * Handles the task change event and updates the selected task.
     * Disconnects from the previous task and sets the new task.
     * 
     * @param {TaskId} task_id - The ID of the selected task.
     * @private
     */
    private task_changed = (task_id: TaskId) => {
        this.disconnect();
        this.selected_task = task_id;
        this.setContent();
    }

    /**
     * Terminates the Control Panel frame and disconnects from the backend.
     * 
     * @private
     */
    private terminate = () => {
        this.disconnect();
        console.log("ControlPanel: Terminate Node");
        ControlPanel.instance = undefined;
    }
}

export default ControlPanel;