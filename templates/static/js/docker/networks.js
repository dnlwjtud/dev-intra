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

    const inspectBtn = createInspectBtn(`${NETWORK_URI_PATH}${networkId}`);
    container.appendChild(inspectBtn);

    const removeBtn = createRemoveBtn();

    if ( isDangling === 'False' ) {
        removeBtn.classList.replace('text-danger','text');
    } else {
        removeBtn.classList.replace('disabled', 'text');
    }

    removeBtn.addEventListener("click", async () => {
        const result = await removeImage(networkId);
        alertRefreshing(result);
    });

    container.appendChild(removeBtn);

    return container;
}

function createNetworkListContextMenu() {

    const container = createMenuContainer(NETWORK_LIST_MENU_ID);

    const buildBtn = createContextMenuItem('Create Network', 'div');
    buildBtn.addEventListener('click', () => {

    });

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
