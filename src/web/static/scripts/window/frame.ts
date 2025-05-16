import EventListener from "../EventListener.js";
import Point from "../point.js";

class Frame {

    static id = 0;

    private frame: HTMLDivElement;
    private header: HTMLDivElement;
    private terminateEvent?: () => void;
    id = Frame.id++;
    kill = null;
    private dragOffsetX: number = 0;
    private dragOffsetY: number = 0;

    /**
     * Basic Frame for all content Objects
     * @param {string} titleText 
     * @param {HTMLElement} contentElement 
     * @param {method} terminate 
     */
    constructor(titleText: string, contentElement?: HTMLElement, terminateEvent?: () => void) {
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
        } else if (contentElement) {
            contentWrapper.textContent = contentElement; // fallback, falls kein Element
        }
        frame.appendChild(contentWrapper);

        this.frame = frame;
        this.header = header;
        this.terminateEvent = terminateEvent;
        this.addEventListeners();
    }

    /**
     * Sets all necessary event listeners
     * @returns {void}
     */
    private addEventListeners(): void {
        EventListener.addEventListener(
            this.header,
            'mousedown',
            (rootEvent: any) => {

                // 🟡 Offset merken
                this.dragOffsetX = rootEvent.clientX - this.frame.offsetLeft;
                this.dragOffsetY = rootEvent.clientY - this.frame.offsetTop;

                EventListener.addEventListener(
                    document,
                    'mousemove',
                    (e: any) => {
                        const mouseEvent = e as MouseEvent;
                        const rawPoint = new Point(
                            mouseEvent.clientX - this.dragOffsetX,
                            mouseEvent.clientY - this.dragOffsetY
                        );
                        const clampedPoint = this.getFramePosition(rawPoint);
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
                    () => {
                        console.log("awd");
                        EventListener.removeAllListeners(`frame-${this.id}-mousemove`);
                    },
                    true,
                    `frame-${this.id}-mousemove`
                );
                EventListener.addEventListener(
                    window,
                    'blur',
                    () => {
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

    /**
     * Gets the current position from the frame
     * @param {Point} point 
     * @returns {Point}
     */
    private getFramePosition(point: Point): Point {

        const playground = document.getElementById('playground');
        if (!playground) {
            return point;
        }
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

    /**
     * Shows the current frame
     * @returns {void}
     */
    public show(): void {
        if (this.frame != undefined) {
            const playground = document.getElementById('playground');
            if (playground) {
                playground.appendChild(this.frame);
            } else {
                console.warn("No element with ID 'playground' found.");
            }
        }
    }

    /**
     * Dispose a frame, removes it from playground and removes all event listeners
     * @returns {void}
     */
    public dispose(): void {
        if (this.frame != undefined) {
            if (this.terminateEvent) {
                this.terminateEvent();
            }
            this.frame.remove()
            EventListener.removeAllListeners(`frame-${this.id}`);
        }
    }
}

export default Frame;