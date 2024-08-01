const NETWORK_MENU_ID = 'network-popup';
const NETWORK_LIST_MENU_ID = 'main-popup';
const NETWORK_URI_PATH = '/dockers/networks'
const NETWORK_API_HOST = `${API_HOST}${NETWORK_URI_PATH}`;

document.addEventListener("click", function(e) {
    clearMenus([NETWORK_MENU_ID, NETWORK_LIST_MENU_ID]);
});

function createNetworkContextMenu(networkId, networkName, isDangling) {
    const container = createMenuContainer(NETWORK_MENU_ID);

    const header = createMenuHeader(networkName);
    container.appendChild(header);

    const inspectBtn = createInspectBtn(`${NETWORK_URI_PATH}/${networkId}`);
    container.appendChild(inspectBtn);

    const removeBtn = createRemoveBtn();

    if ( isDangling === 'False' ) {
        removeBtn.classList.replace('text-danger','text');
    } else {
        removeBtn.classList.replace('disabled', 'text');
    }

    removeBtn.addEventListener("click", async () => {
        const result = await removeDockerNetwork(networkId);

        if (result === null) {
            alertRefreshing({});
        } else {
            alertErrorMsg(true);
        }
    });

    container.appendChild(removeBtn);

    return container;
}

function createNetworkListContextMenu() {

    const container = createMenuContainer(NETWORK_LIST_MENU_ID);

    const buildBtn = createContextMenuItem('Create Network', 'a');
    buildBtn.href = `${NETWORK_URI_PATH}/new`;

    container.appendChild(buildBtn);

    return container;
}

function handleNetworkMenu(e, networkId, networkName, isDangling) {

    e.preventDefault();
    e.stopPropagation();

    clearMenus([NETWORK_MENU_ID, NETWORK_LIST_MENU_ID]);

    const imageMenu = createNetworkContextMenu(networkId, networkName, isDangling);

    appearMenu(e, imageMenu);

}

function handleListMenu(e) {
    e.preventDefault();

    clearMenus([NETWORK_MENU_ID, NETWORK_LIST_MENU_ID]);
    const listContextMenu = createNetworkListContextMenu();

    appearMenu(e, listContextMenu);

}

async function handleCreateBtnEvent(e) {
    e.preventDefault();

    const form = document.getElementById('create-network-form');

    const driverEl = document.getElementById('driver');
    const driver = driverEl.value;

    const nameEl = document.getElementById('name');
    const name = nameEl.value

    if (!name) {
        form.classList.add('was-validated');
        nameEl.focus();
        return;
    }

    const result = await createDockerNetwork({ driver, name })

    if ( result && result.status === 201 ) {
        alert(result.msg);
        location.replace('/dockers/networks');
        return;
    }

    alertErrorMsg(true);

}

async function createDockerNetwork(data) {

    if (!data) return null;

    return fetch(`${NETWORK_API_HOST}/new`,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then( resp => {
        if ( resp.status >= 400 ) {
            return null;
        } else {
            return resp.json();
        }
    }).catch( err => {
        console.log(err);
        return null;
    });

}

async function removeDockerNetwork(networkId) {

    if (!networkId) return undefined;

    return fetch(`${NETWORK_API_HOST}/${networkId}`,{
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
    }).then( resp => {
        console.log(resp);
        if ( resp.status >= 400 ) {
            return resp.json();
        } else {
            return null;
        }
    }).catch( err => {
        console.log(err);
        return null;
    });

}
