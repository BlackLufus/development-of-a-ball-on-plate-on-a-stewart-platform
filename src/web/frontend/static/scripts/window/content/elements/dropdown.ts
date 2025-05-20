class DropdownItemError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "DropdownItemError";
        Object.setPrototypeOf(this, DropdownItemError.prototype);
    }
}

export class DropdownItem {

    public id: any;
    public name: string;

    constructor(id: any, name: string) {
        this.id = id;
        this.name = name;
    }
}

class Dropdown {

    public readonly element: HTMLElement;

    constructor(values: Array<DropdownItem>, selectEvent: (value: DropdownItem, index: number) => void, index: number=0) {
        this.element = document.createElement('div');

        this.build(values, selectEvent, index);
    }

    private build(values: Array<DropdownItem>, selectEvent: (value: DropdownItem, index: number) => void, index: number): void {
        this.element.className = 'select_dropdown_container';

        const select = document.createElement('select');
        select.className = 'select_dropdown_list';
        select.addEventListener(
            'change',
            () => {
                selectEvent(values[select.selectedIndex], select.selectedIndex);
            }
        )
        this.element.appendChild(select);

        values.forEach((value, index) => {
            const option = document.createElement('option');
            option.className = 'select_dropdown_item'
            option.value = value.id;
            option.text = value.name;
            select.appendChild(option);
        });
        select.selectedIndex = index;
    }
}

export default Dropdown;