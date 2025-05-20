import EventListener from "../EventListener.js";
import Point from "../point.js";

class FrameError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "FrameError";
        Object.setPrototypeOf(this, FrameError.prototype);
    }
}

class Frame {

    private static zCounter: number = 1000;
    private static id = 0;

    private frame: HTMLDivElement;
    private header: HTMLDivElement;
    private terminateEvent?: () => void;
    protected id = Frame.id++;
    private dragOffsetX: number = 0;
    private dragOffsetY: number = 0;

    /**
     * Basic Frame for all content Objects
     * @param {string} titleText 
     * @param {HTMLElement} contentElement 
     * @param {method} terminateEvent 
     */
    constructor(titleText: string, contentElement?: HTMLElement, terminateEvent?: () => void) {
        this.frame = document.createElement('div');
        this.frame.className = 'frame';
        this.frame.style.zIndex = (Frame.zCounter++).toString();

        this.header = document.createElement('div');
        this.header.className = "frame_header";
        this.frame.appendChild(this.header);

        const title = document.createElement('span');
        title.className = "frame_title";
        title.textContent = titleText;
        this.header.appendChild(title);

        const close_button = document.createElement('button');
        close_button.className = "frame_close";
        close_button.addEventListener("click", () => this.dispose());
        this.header.appendChild(close_button);

        const contentWrapper = document.createElement('div');
        contentWrapper.className = "frame_content";
        if (contentElement instanceof HTMLElement) {
            contentWrapper.appendChild(contentElement);
        } else if (contentElement) {
            contentWrapper.textContent = contentElement; // fallback, falls kein Element
        }
        this.frame.appendChild(contentWrapper);

        this.terminateEvent = terminateEvent;
        this.addEventListeners();
    }

    /**
     * Sets all necessary event listeners
     * @returns {void}
     */
    private addEventListeners(): void {
        EventListener.addEventListener(
            this.frame,
            'mousedown',
            this.focus,
            false,
            `frame-${this.id}`
        )
        EventListener.addEventListener(
            this.header,
            'mousedown',
            (rootEvent: any) => {

                this.focus(rootEvent);

                // 🟡 Offset merken
                this.dragOffsetX = rootEvent.clientX - this.frame.offsetLeft;
                this.dragOffsetY = rootEvent.clientY - this.frame.offsetTop;

                EventListener.addEventListener(
                    document,
                    'mousemove',
                    (e: MouseEvent) => {
                        const rawPoint = new Point(
                            e.clientX - this.dragOffsetX,
                            e.clientY - this.dragOffsetY
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
                        EventListener.removeAllListeners(`frame-${this.id}-mousemove`);
                    },
                    true,
                    `frame-${this.id}-mousemove`
                );
                EventListener.addEventListener(
                    window,
                    'blur',
                    () => {
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
            throw new FrameError("No element with ID 'playground' found.");
        }
        if (point.x < 0) {
            point.x = 0;
        }
        else if (point.x > playground.offsetWidth - this.header.offsetWidth) {
            point.x = playground.offsetWidth - this.header.offsetWidth;
        }
        if (point.y < 0) {
            point.y = 0;
        }
        else if (point.y > playground.offsetHeight - this.header.offsetHeight) {
            point.y = playground.offsetHeight - this.header.offsetHeight;
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
            if (!playground) {
                throw new FrameError("No element with ID 'playground' found.");
            }
            else if (playground.contains(this.frame)) {
                throw new FrameError("Frame already in playground");
            }
            else {
                playground.appendChild(this.frame);
            }
        }
    }

    public focus(event: MouseEvent): void {
        const target = event.target as HTMLElement;
        const frame = target.closest('.frame') as HTMLElement | null;

        if (frame && frame.style.zIndex != `${Frame.zCounter-1}`) {
            console.log(`zIndex: ${frame.style.zIndex}`)
            frame.style.zIndex = (Frame.zCounter++).toString();
        }
    }

    /**
     * Dispose a frame, removes it from playground and removes all event listeners
     * @returns {void}
     */
    public dispose(): void {
        if (this.frame) {
            if (this.terminateEvent) {
                this.terminateEvent();
            }
            this.frame.remove()
            EventListener.removeAllListeners(`frame-${this.id}`);
        }
    }
}

export default Frame;