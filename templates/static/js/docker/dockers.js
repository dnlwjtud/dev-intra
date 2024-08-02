document.addEventListener("contextmenu", function(e) {
    e.preventDefault();
});

function clearMenus(menuNames) {
    menuNames.forEach(n => clearMenu(n));
}

function createContextMenuItem(name, type) {
    const item = document.createElement(type);

    item.classList.add('list-group-item', 'list-group-item-action');

    item.style.cursor = 'default';
    item.innerText = name;

    return item;
}

function createMenuContainer(componentId) {
    const container = document.createElement('div');

    container.classList.add('list-group', 'list-group-flush');
    container.id = componentId;
    container.style.width = '250px';

    return container;
}

function appearMenu(e, menu) {
    menu.style.position = 'absolute';
    menu.style.left = e.clientX + 'px';
    menu.style.top = e.clientY + 'px';
    menu.style.zIndex = 100;
    menu.style.display = 'block';

    document.querySelector(ROOT).appendChild(menu);
}

function clearMenu(componentId) {
    const existingMenu = document.querySelector(`#${componentId}`);

    if (existingMenu) {
        existingMenu.style.display = 'none';
        existingMenu.remove();
    }

}

function alertRefreshing(result) {
    if (result === null) {
        alertErrorMsg(true);
        return;
    }

    if ( result.msg ) {
        alert(result.msg);
    } else {
        alert('Successfully done.');
    }
    location.reload();
}

function createMenuHeader(headerText) {
    const header = createContextMenuItem(headerText, 'div');
    header.classList.add('disabled', 'text-primary');
    return header;
}

function createInspectBtn(targetPath) {
    const inspectBtn = createContextMenuItem('Inspect', 'a');
    inspectBtn.href = targetPath;
    return inspectBtn;
}

function createRemoveBtn() {
    const removeBtn = createContextMenuItem('Remove', 'div');
    removeBtn.classList.add('text-danger', 'disabled');
    return removeBtn;
}

function handleRemoveBtnEvent(targetId) {

    const targetEl = document.getElementById(targetId);

    const selectedEls = targetEl.selectedOptions;
    const selectedAry = Array.from(selectedEls);

    selectedAry.forEach(i => targetEl.removeChild(i));

}