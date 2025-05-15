import Frame from './window/frame.js';

const darkModeSwitch = document.getElementById('dark-mode');
darkModeSwitch.addEventListener('change', function() {
    UI.updateDarkMode();
});

const element1 = document.getElementById('element_1');
element1.addEventListener('click', () => {
    const frame = new Frame('Hallo', "null");
    frame.show()
});

class UI {

    static init() {
    }

    // Function to update the dark mode
    static updateDarkMode() {
        document.documentElement.setAttribute('data-theme', darkModeSwitch.checked ? 'dark' : 'light');
    }

    // Funktion, um die Position relativ zum Container abzufragen
        static getRelativePosition(inputX, inputY, radius = 20) {
            //console.log(inputX, inputY);
            // Get offset of the container (left, top)
            //console.log(rect);
            //return { x: inputX - 20, y: inputY - 20 };
            //console.log(`inputX: ${inputX}, inputY: ${inputY}`);
            //console.log(`left: ${container.offsetLeft}, top: ${container.offsetTop}`);
            let x = parseInt(inputX);
            let y = parseInt(inputY);
            if (x < 10) {
                x = 10;
            }
            else if (x > playground.offsetWidth - (radius * 2) - 10) {
                x = playground.offsetWidth - (radius * 2) - 10;
            }
            if (y < 10) {
                y = 10;
            }
            else if (y > playground.offsetHeight - (radius * 2) - 20) {
                y = playground.offsetHeight - (radius * 2) - 20;
            }
            //console.log(`x: ${x}, y: ${y}`);
            return { x: x, y: y};
        }
}

export default UI;