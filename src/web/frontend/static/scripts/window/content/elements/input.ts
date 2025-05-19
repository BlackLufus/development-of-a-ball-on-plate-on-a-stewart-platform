import Dropdown, { DropdownItem } from "./dropdown.js";

class InputError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "InputError";
        Object.setPrototypeOf(this, InputError.prototype);
    }
}

export enum InputType {
    TEXT = 'text',
    NUMBER = 'number',
    DROPDOWN = 'dropdown'
}

class Input {

    public readonly element: HTMLElement;
    constructor(id: any, name: string, values: Record<string, any>) {
        this.element = document.createElement('div');

        this.build(id, name, values);
    }

    private build(id: any, name: string, values: Record<string, any>): void {
        this.element.classList = 'input_element';

        const argument_div = document.createElement('div');
        const argument = document.createElement('span');
        argument.textContent = name;
        argument_div.appendChild(argument);
        this.element.appendChild(argument_div);

        const input_div = document.createElement('div');
        const input = document.createElement('input');
        input_div.appendChild(input);
        if (values[id].type == InputType.DROPDOWN) {
            console.log(values[id].list[values[id].value]);
            input.type = 'text';
            input.value = values[id].list[values[id].index].name;
            input.readOnly = true;
            const dropdown = new Dropdown(
                values[id].list,
                (item: DropdownItem, index: number) => {
                    values[id].value = item.id;
                    input.value = item.name;
                    values[id].index = index;
                }
            );
            input.addEventListener(
                'click',
                () => {
                    dropdown.toggle();
                }
            );
            input_div.appendChild(dropdown.element);
        }
        else {
            input.type = values[id].type;
            input.value = values[id].value;
            input.min = values[id].min;
            input.max = values[id].max;
            input.step = values[id].step;
            input.addEventListener(
                'change',
                () => {
                    values[id]['value'] = values[id].type == InputType.NUMBER ? Number(input.value) : input.value;
                }
            )
        }
        this.element.appendChild(input_div);
    }
}

export default Input;