// ==UserScript==
// @name Safeway
// @match https://www.safeway.com/erums/cart/*
// @run-at document-idle
// ==/UserScript==

function getProductId(productElement) {
    const id = productElement.querySelector('[id*=itemname]')
        .id.replace(/^itemname/, '');

    console.log('Product ID:', id);
    return id;
}

function makeProductStorageKey(id) {
    return 'pid:' + id;
}

function setAngularInputValue(inputElement, value) {
    inputElement.value = value;
    inputElement.dispatchEvent(new Event('input', {bubbles: true}));
}

function prepareProductNote(product, id) {
    const noteInput = product.querySelector(
        '.item-preference-card input[type=text]');
    let note = noteInput.value;

    if (note !== '') {
        console.log('Note already present:', note);
        return;
    }

    note = localStorage.getItem(makeProductStorageKey(id));

    if (note !== null) {
        console.log('Got saved product note:', note);
    }
    else {
        note = 'Replacement allowed: ';
        console.log('Using default product note:', note);
    }

    setAngularInputValue(noteInput, note);
}

function openProductNote(product) {
    product.querySelector('[aria-expanded=false]').click();
}

function prepareProductNotes(products) {
    products.forEach(product => {
        const id = getProductId(product);
        prepareProductNote(product, id);
        openProductNote(product);
    });
}

const angularLoadCheckIntervalId = setInterval(() => {
    const productElements = document.querySelectorAll('app-full-cart-item');

    if (productElements.length > 0) {
        prepareProductNotes(productElements);
        clearInterval(angularLoadCheckIntervalId);
    } else {
        console.log('Angular not yet loaded...');
    }
}, 500);
