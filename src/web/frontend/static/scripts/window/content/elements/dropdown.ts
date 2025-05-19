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
    private is_show: boolean = false;

    constructor(values: Array<DropdownItem>, selectEvent: (value: DropdownItem, index: number) => void) {
        this.element = document.createElement('div');

        this.build(values, selectEvent);
    }

    private build(values: Array<DropdownItem>, selectEvent: (value: DropdownItem, index: number) => void): void {
        this.element.className = 'select_dropdown_container';
        this.element.style.display = 'none';

        const list = document.createElement('div');
        list.className = 'select_dropdown_list';
        this.element.appendChild(list);

        values.forEach((value, index) => {
            const item = document.createElement('div');
            item.className = 'select_dropdown_item'
            item.addEventListener(
                'click',
                () => {
                    selectEvent(value, index);
                    this.toggle();
                }
            )
            list.appendChild(item);

            const name = document.createElement('span');
            name.className = 'select_dropdown_item_name';
            name.textContent = value.name;
            item.appendChild(name);
        });
    }

    public toggle(): void {
        if (this.is_show) {
            this.is_show = false;
            this.element.style.display = 'none';
        }
        else {
            this.is_show = true;
            this.element.style.display = 'block';
        }
    }
}

export default Dropdown;