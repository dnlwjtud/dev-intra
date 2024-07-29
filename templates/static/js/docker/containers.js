const CONTAINER_MENU_ID = 'container-popup';
const CONTAINER_LIST_MENU_ID = 'main-popup';

document.addEventListener("contextmenu", function(e) {
    e.preventDefault();
});

function clearMenus(menuNames) {
    menuNames.forEach(n => clearMenu(n));
}

document.addEventListener("click", function(e) {
    clearMenus([CONTAINER_MENU_ID, CONTAINER_LIST_MENU_ID]);
});

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

function createContainerContextMenu(containerId, containerState) {

    const CONTEXT_MENU_NAME = [ 'Start', 'Restart', 'Stop', 'Pause', 'Unpause', 'Reload'];

    const container = createMenuContainer(CONTAINER_MENU_ID);

    const header = createContextMenuItem(containerId, 'div');
    header.classList.add('disabled', 'text-primary');

    container.appendChild(header);

    if (containerState === 'running' ) {
        const connectBtn = createContextMenuItem('Connect', 'div');
        connectBtn.classList.add('text-success');
        connectBtn.addEventListener("click", () => {

        });

        container.appendChild(connectBtn);
    }

    const inspectBtn = createContextMenuItem('Inspect', 'a');
    inspectBtn.href = `/containers/${containerId}`;

    container.appendChild(inspectBtn);

    CONTEXT_MENU_NAME.forEach(
        n => {
            const menuItem = createContextMenuItem(n, 'div');

            if ( containerState === 'running' ) {
                if ( n === 'Start' || n === 'Unpause') {
                    menuItem.classList.add('disabled');
                }
            } else if ( containerState === 'paused' ) {
                if ( n === 'Start' || n === 'Pause' ||  n === 'Restart' ) {
                    console.log("PAUSED")
                    menuItem.classList.add('disabled');
                }
            } else if ( containerState === 'exited' ) {
                if ( n === 'Pause' || n === 'Unpause' ||  n === 'Restart' || n === 'Stop' ) {
                    menuItem.classList.add('disabled');
                }
            } else {
                if ( n !== 'Stop' ) {
                    menuItem.classList.add('disabled');
                }
            }

            menuItem.addEventListener("click", () => {

            })

            container.appendChild(menuItem);
        }
    );

    const removeBtn = createContextMenuItem('Remove', 'div');
    removeBtn.classList.add('text-danger', 'disabled');
    removeBtn.classList.replace('text-danger', 'text');

    if (containerState !== 'running') {
        removeBtn.classList.replace('text', 'text-danger')
        removeBtn.classList.replace('disabled', 'text')
    }

    removeBtn.addEventListener("click", () => {

    });

    container.appendChild(removeBtn);

    return container;

}

function appearMenu(e, menu) {
    menu.style.position = 'absolute';
    menu.style.left = e.clientX + 'px';
    menu.style.top = e.clientY + 'px';
    menu.style.zIndex = 100;
    menu.style.display = 'block';
}

function clearMenu(componentId) {
    const existingMenu = document.querySelector(`#${componentId}`);

    if (existingMenu) {
        existingMenu.style.display = 'none';
        existingMenu.remove();
    }

}

function handleContainerMenu(e, containerId, containerState) {

    // preventing events
    e.preventDefault();
    e.stopPropagation();

    // clear menu
    clearMenus([CONTAINER_MENU_ID, CONTAINER_LIST_MENU_ID]);

    // create menu
    const popMenu = createContainerContextMenu(containerId, containerState);

    // appear menu
    appearMenu(e, popMenu);
    document.querySelector(ROOT)
        .appendChild(popMenu);

}

function handleListMenu(e) {
    e.preventDefault();

    clearMenus([CONTAINER_MENU_ID, CONTAINER_LIST_MENU_ID]);

    const menuContainer = createMenuContainer(CONTAINER_LIST_MENU_ID);

    const createConBtn = createContextMenuItem('New container', 'div');

    createConBtn.addEventListener("click", () =>{

    });

    menuContainer.appendChild(createConBtn);

    appearMenu(e, menuContainer);

    document.querySelector(ROOT)
        .appendChild(menuContainer);
}
