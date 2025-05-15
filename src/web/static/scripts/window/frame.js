import EventListener from "../EventListener.js";
import Point from "../point.js";
import UI from "../ui.js";

class Frame {

    static id = 0;

    frame = undefined;
    header = undefined;
    id = Frame.id++;

    constructor(titleText, contentElement) {
        const frame = document.createElement('div');
        frame.className = 'frame';

        const header = document.createElement('div');
        header.className = "frame_header";
        frame.appendChild(header);

        const title = document.createElement('span');
        title.className = "frame_title";
        title.textContent = titleText;
        header.appendChild(title);

        const close_button = document.createElement('button');
        close_button.className = "frame_close";
        close_button.addEventListener("click", () => this.dispose());
        header.appendChild(close_button);

        const contentWrapper = document.createElement('div');
        contentWrapper.className = "frame_content";
        if (contentElement instanceof HTMLElement) {
            contentWrapper.appendChild(contentElement);
        } else {
            contentWrapper.textContent = contentElement; // fallback, falls kein Element
        }
        frame.appendChild(contentWrapper);

        this.frame = frame;
        this.header = header;
        this.addEventListeners();
    }

    addEventListeners() {
        EventListener.addEventListener(
            this.header,
            'mousedown',
            (rootEvent) => {

                // 🟡 Offset merken
                this.dragOffsetX = rootEvent.clientX - this.frame.offsetLeft;
                this.dragOffsetY = rootEvent.clientY - this.frame.offsetTop;

                EventListener.addEventListener(
                    document,
                    'mousemove',
                    (e) => {
                        const rawPoint = new Point(
                            e.clientX - this.dragOffsetX,
                            e.clientY - this.dragOffsetY
                        );
                        const clampedPoint = this.getNodeMenuPosition(rawPoint);
                        this.frame.style.left = `${clampedPoint.x}px`;
                        this.frame.style.top = `${clampedPoint.y}px`;
                    },
                    false,
                    `frame-${this.id}-mousemove`,
                    { passive: false },
                );

                EventListener.addEventListener(
                    window,
                    'mouseup',
                    (e) => {
                        console.log("awd");
                        EventListener.removeAllListeners(`frame-${this.id}-mousemove`);
                    },
                    true,
                    `frame-${this.id}-mousemove`
                );
                EventListener.addEventListener(
                    window,
                    'blur',
                    (e) => {
                        console.log("awd");
                        EventListener.removeAllListeners(`frame-${this.id}-mousemove`);
                    },
                    true,
                    `frame-${this.id}-mousemove`
                );
            },
            false,
            `frame-${this.id}`
        );
    }

    getNodeMenuPosition(point) {

        const playground = document.getElementById('playground');
        if (point.x < 0) {
            point.x = 0;
        }
        else if (point.x > playground.offsetWidth - this.frame.offsetWidth) {
            point.x = playground.offsetWidth - this.frame.offsetWidth;
        }
        if (point.y < 0) {
            point.y = 0;
        }
        else if (point.y > playground.offsetHeight - this.frame.offsetHeight) {
            point.y = playground.offsetHeight - this.frame.offsetHeight;
        }
        return point;
    }

    setPosition(x, y) {
        this.x = parseInt(x);
        this.y = parseInt(y);
        if (this.frame != undefined) {
            this.frame.style.left = `${this.x}px`;
            this.frame.style.top = `${this.y}px`;
        }
    }

    show() {
        if (this.frame != undefined) {
            const playground = document.getElementById('playground');
            if (playground) {
                playground.appendChild(this.frame);
            } else {
                console.warn("No element with ID 'playground' found.");
            }
        }
    }

    dispose() {
        if (this.frame != undefined) {
            this.frame.remove()
            EventListener.removeAllListeners(`frame-${this.id}`);
        }
    }
}

export default Frame;