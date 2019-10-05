// ==UserScript==
// @name Shipt
// @match https://shop.shipt.com/cart
// @run-at document-idle
// ==/UserScript==

const saveNoteCallbacks = [];

document.querySelectorAll('*[data-test=CartProduct-product-card]').forEach(product => {
    const editNoteButton = product.querySelector(
        'button[data-test=CartProduct-edit-note-button]');
    const notesInput = product.querySelector('textarea');

    if (editNoteButton) {
        editNoteButton.click();
    }
    else {
        product.querySelector('button[data-test=CartProduct-add-note-button]').click();
        notesInput.value = 'Replacement allowed: ';
    }

    const saveNote = () => {
        const saveNoteButton = product.querySelector(
            'button[data-test=CartProduct-update-note-button]');

        if (saveNoteButton) {
            saveNoteButton.click();
        }
    };

    notesInput.addEventListener('keyup', event => {
        const isSaveShortcut
            = event.ctrlKey
            && ((event.keyCode === '\n'.charCodeAt(0))
                || (event.keyCode === '\r'.charCodeAt(0)));

        if (isSaveShortcut) {
            saveNote();
        }
    });

    saveNoteCallbacks.push(saveNote);
});

const saveAllNotesButton = document.createElement('button');
saveAllNotesButton.textContent = 'Save all instructions';

saveAllNotesButton.addEventListener('click', event => {
    event.preventDefault();
    saveNoteCallbacks.forEach(callback => callback());
});

document.querySelector('h1').appendChild(saveAllNotesButton);
