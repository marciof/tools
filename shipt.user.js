// ==UserScript==
// @name Shipt
// @match https://shop.shipt.com/*
// @run-at document-idle
// ==/UserScript==

/**
 * @see https://github.com/facebook/react/blob/master/packages/react-devtools-shared/src/backend/views/Highlighter/Overlay.js
 */
function getReactComponent(element) {
    for (const prop in element) {
        if (!element.hasOwnProperty(prop)) {
            continue;
        }
        if (prop.startsWith('__reactInternalInstance')) {
            const fiberNode = element[prop];
            return fiberNode && fiberNode.return && fiberNode.return.stateNode;
        }
    }
    throw new Error('No React Component found: ' + element);
}

function addSaveNoteKeyboardShortcut(element, saveCallback) {
    element.addEventListener('keyup', event => {
        if (!event.ctrlKey) {
            return;
        }

        const key = String.fromCharCode(event.keyCode);

        if (/[\n\r]/.test(key)) {
            saveCallback();
        }
    });
}

/**
 * @see https://reactjs.org/docs/react-component.html#setstate
 */
function enhanceProductCard(component, element) {
    component.setState(
        function updateState(state) {
            if (state.note.trim() !== '') {
                return {};
            }
            console.log('Setting default product note', component);
            return {
                isEditingNote: true,
                note: 'Replacement allowed: ',
            };
        },
        function onReRender() {
            addSaveNoteKeyboardShortcut(element, function save() {
                console.log('Saving product note', component);
                element.querySelector('*[data-test=CartProduct-update-note-button]')
                    .click();
            });
        },
    );
}

function toArray(arrayLike) {
    return Array.from(arrayLike);
}

function mergeArrays(left, right) {
    return Array.concat(left, right);
}

const observer = new MutationObserver(mutations => {
    if (location.pathname !== '/cart') {
        console.log('Skipping, not in the cart page');
        return;
    }

    return mutations.map(mutation => mutation.addedNodes)
        .map(toArray)
        .reduce(mergeArrays, [])
        .filter(node => node.nodeType === Node.ELEMENT_NODE)
        .map(node => node.querySelectorAll('*[data-test=CartProduct-product-card]'))
        .map(toArray)
        .reduce(mergeArrays, [])
        .forEach(productEl => {
            console.log('Found product card element', productEl);
            const productComp = getReactComponent(productEl);

            console.log('Found product React component', productComp);
            enhanceProductCard(productComp, productEl);
        });
});

observer.observe(document, {
    childList: true,
    subtree: true,
});
