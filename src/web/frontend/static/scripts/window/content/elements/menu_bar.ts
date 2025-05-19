class MenuBarError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "MenuBarError";
        Object.setPrototypeOf(this, MenuBarError.prototype);
    }
}

export class MenuBarItem {

    public id: any;
    public name: string;

    constructor(id: any, name: string) {
        this.id = id;
        this.name = name;
    }
}

class MenuBar {

    private static id: number = 0;
    private list: Array<MenuBarItem>;
    private clickEvent: (id: any) => void;
    public readonly element: HTMLElement;

    constructor(list: Array<MenuBarItem>, clickEvent: (id: any) => void, checked_index: number = 0) {
        if (list.length == 0) {
            throw new MenuBarError(`List is emtpy but a list requires at least 1 item.`);
        }
        if (checked_index < 0 || checked_index > list.length) {
            throw new MenuBarError(`Checked index ${checked_index} is out of range, possible range is between 0 and ${list.length - 1}.`);
        }
        this.list = list;
        this.clickEvent = clickEvent;

        this.element = document.createElement('div');

        this.build(checked_index);
    }

    private build(checked_index: number): void {
        this.element.classList = 'menu_bar';
        
        this.list.forEach((item, index) => {
            const menu_bar_item = document.createElement('div');
            menu_bar_item.className = 'menu_bar_item';
            this.element.appendChild(menu_bar_item);

            const item_checkbox = document.createElement('input');
            item_checkbox.type = 'radio';
            item_checkbox.name = `menu_option_${MenuBar.id}`;
            if (checked_index == index) {
                item_checkbox.checked = true;
            }
            menu_bar_item.addEventListener(
                'click',
                (e: MouseEvent) => {
                    item_checkbox.checked = true;
                    this.clickEvent(item.id);
                }
            )
            menu_bar_item.appendChild(item_checkbox);

            const item_name = document.createElement('span');
            item_name.textContent = item.name;
            menu_bar_item.appendChild(item_name);
        });
    }
}

export default MenuBar;