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

function addSaveNoteKeyboardShortcut(productEl, saveCallback) {
    productEl.addEventListener('keyup', event => {
        if (!event.ctrlKey) {
            return;
        }

        const key = String.fromCharCode(event.keyCode);

        if (/[\n\r]/.test(key)) {
            saveCallback();
        }
    });
}

function getSaveButton(productEl) {
    return productEl.querySelector('*[data-test=CartProduct-update-note-button]');
}

function makeProductKey(id) {
    return 'pid:' + id;
}

function prepareProductNote(id, note) {
    if (note !== '') {
        console.log('Product note already present:', note);
        return note;
    }

    note = localStorage.getItem(makeProductKey(id));

    if (note !== null) {
        console.log('Got saved product note:', note);
        return note;
    }

    note = 'Replacement allowed: ';
    console.log('Setting default product note:', note);
    return note;
}

/**
 * @see https://reactjs.org/docs/react-component.html#setstate
 */
function enhanceProductCard(component, element) {
    const { id, name } = component.props.product;
    console.log('Enhancing product ID', id, 'named:', name);

    component.setState(
        function updateState(state) {
            return {
                isEditingNote: true,
                note: prepareProductNote(id, state.note),
            };
        },
        function onReRender() {
            getSaveButton(element).addEventListener('click', () => {
                console.log('Saving product note:', component.state.note);
                localStorage.setItem(makeProductKey(id), component.state.note);
            });

            addSaveNoteKeyboardShortcut(element, () => {
                console.log('Save product note keyboard shortcut');
                getSaveButton(element).click();
            });
        },
    );
}

function toArray(arrayLike) {
    return Array.from(arrayLike);
}

function arrayReducer(left, right) {
    return left.concat(right);
}

const observer = new MutationObserver(mutations => {
    if (location.pathname !== '/cart') {
        console.log('Skipping, not in the cart page');
        return;
    }

    return mutations.map(mutation => mutation.addedNodes)
        .map(toArray)
        .reduce(arrayReducer, [])
        .filter(node => node.nodeType === Node.ELEMENT_NODE)
        .map(el => el.querySelectorAll('*[data-test=CartProduct-product-card]'))
        .map(toArray)
        .reduce(arrayReducer, [])
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
