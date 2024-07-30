const IMAGE_MENU_ID = 'container-popup';
const IMAGE_LIST_MENU_ID = 'main-popup';
const IMAGE_API_HOST = `${API_HOST}/dockers/images`;

document.addEventListener("click", function(e) {
    clearMenus([IMAGE_MENU_ID, IMAGE_LIST_MENU_ID]);
});

function createImageContextMenu(imageName) {
    const container = createMenuContainer(IMAGE_MENU_ID);

    const header = createMenuHeader(imageName);
    container.appendChild(header);

    const inspectBtn = createInspectBtn(`/dockers/images/${imageName}`);
    container.appendChild(inspectBtn);

    const removeBtn = createRemoveBtn();

    removeBtn.addEventListener("click", () => {

    });

    container.appendChild(removeBtn);

    return container;
}

function createImageListContextMenu() {

    const container = createMenuContainer(IMAGE_LIST_MENU_ID);

    const buildBtn = createContextMenuItem('Build Image', 'div');
    buildBtn.addEventListener('click', () => {

    });

    container.appendChild(buildBtn);

    return container;
}

function handleImageMenu(e, imageName) {

    e.preventDefault();
    e.stopPropagation();

    clearMenus([IMAGE_MENU_ID, IMAGE_LIST_MENU_ID]);

    const imageMenu = createImageContextMenu(imageName);

    appearMenu(e, imageMenu);

}

function handleListMenu(e) {
    e.preventDefault();

    clearMenus([IMAGE_MENU_ID, IMAGE_LIST_MENU_ID]);

    const listContextMenu = createImageListContextMenu();

    appearMenu(e, listContextMenu);

}


