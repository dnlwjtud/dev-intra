const CONTAINER_MENU_ID = 'container-popup';
const CONTAINER_LIST_MENU_ID = 'main-popup';
const CONTAINER_API_HOST = `${API_HOST}/dockers/containers`;

document.addEventListener("click", function(e) {
    clearMenus([CONTAINER_MENU_ID, CONTAINER_LIST_MENU_ID]);
});


function createContainerContextMenu(containerId, containerState) {

    const CONTEXT_MENU_NAME = [ 'Start', 'Restart', 'Stop', 'Pause', 'Unpause', 'Reload'];

    const container = createMenuContainer(CONTAINER_MENU_ID);

    const header = createMenuHeader(containerId);
    container.appendChild(header);

    if (containerState === 'running') {
        const connectBtn = createContextMenuItem('Connect', 'div');
        connectBtn.classList.add('text-success');
        connectBtn.addEventListener("click", () => {

        });

        container.appendChild(connectBtn);
    }

    const inspectBtn = createInspectBtn(`/dockers/containers/${containerId}`);
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
                if ( n !== 'Start' ) {
                    menuItem.classList.add('disabled');
                }
            } else {
                if ( n !== 'Stop' ) {
                    menuItem.classList.add('disabled');
                }
            }

            menuItem.addEventListener("click", async () => {
                const result = await updateContainerStatus(containerId, n);
                alertRefreshing(result);
            });

            container.appendChild(menuItem);
        }

    );

    const removeBtn = createRemoveBtn();
    removeBtn.classList.replace('text-danger', 'text');

    if (containerState !== 'running') {
        removeBtn.classList.replace('text', 'text-danger')
        removeBtn.classList.replace('disabled', 'text')
    }

    removeBtn.addEventListener("click", async () => {
        const result = await removeContainer(containerId);
        alertRefreshing(result);
    });

    container.appendChild(removeBtn);

    return container;

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
}

function createContainerListContextMenu() {
    const menuContainer = createMenuContainer(CONTAINER_LIST_MENU_ID);

    const createConBtn = createContextMenuItem('Run container', 'a');
    createConBtn.href = '/dockers/containers/new';

    menuContainer.appendChild(createConBtn);

    return menuContainer;
}

function handleListMenu(e) {
    e.preventDefault();

    clearMenus([CONTAINER_MENU_ID, CONTAINER_LIST_MENU_ID]);

    const menuContainer = createContainerListContextMenu();

    appearMenu(e, menuContainer);
}

async function updateContainerStatus(containerId, actType) {
    const req = {
        act_type: actType
    };

    return fetch(`${CONTAINER_API_HOST}/${containerId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(req)
    })
    .then(resp => {
        if ( resp.status >= 400 ) {
            return null;
        } else {
             return resp.json();
        }
    })
    .catch((err) => {
        console.log(err);
        return null;
    });
}

async function removeContainer(containerId) {
    return fetch(`${CONTAINER_API_HOST}/${containerId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'force': false
        })
    })
    .then(resp => {
        if ( resp.status >= 400 ) {
            return null;
        } else {
            return true;
        }
    })
    .catch((err) => {
        console.log(err);
        return null;
    });
}

