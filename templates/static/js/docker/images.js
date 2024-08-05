const IMAGE_MENU_ID = 'image-popup';
const IMAGE_LIST_MENU_ID = 'main-popup';
const DOCKERFILE_MENU_ID = 'dockerfile-popup';
const IMAGE_API_HOST = `${API_HOST}/dockers/images`;

document.addEventListener("click", function(e) {
    clearMenus([IMAGE_MENU_ID, IMAGE_LIST_MENU_ID, DOCKERFILE_MENU_ID]);
});

function createImageContextMenu(imageId, imageName, isUsed) {
    const container = createMenuContainer(IMAGE_MENU_ID);

    const header = createMenuHeader(imageName);
    container.appendChild(header);

    const inspectBtn = createInspectBtn(`/dockers/images/${imageId}`);
    container.appendChild(inspectBtn);

    const removeBtn = createRemoveBtn();

    if ( isUsed === 'True' ) {
        removeBtn.classList.replace('text-danger','text');
    } else {
        removeBtn.classList.replace('disabled', 'text');
    }

    removeBtn.addEventListener("click", async () => {
        const result = await removeImage(imageId);
        console.log(result);
        alertRefreshing(result);
    });

    container.appendChild(removeBtn);

    return container;
}

function createImageListContextMenu() {

    const container = createMenuContainer(IMAGE_LIST_MENU_ID);

    const pullBtn = createContextMenuItem('Pull Image', 'div');
    pullBtn.addEventListener('click', () => {

    });

    const buildBtn = createContextMenuItem('Create Dockerfile', 'a');
    buildBtn.href = '/dockers/images/new';

    container.appendChild(pullBtn);
    container.appendChild(buildBtn);

    return container;
}

function handleImageMenu(e, imageId, imageName, isUsed) {

    e.preventDefault();
    e.stopPropagation();

    clearMenus([IMAGE_MENU_ID, IMAGE_LIST_MENU_ID]);

    const imageMenu = createImageContextMenu(imageId, imageName, isUsed);

    appearMenu(e, imageMenu);

}

function handleListMenu(e) {
    e.preventDefault();

    clearMenus([IMAGE_MENU_ID, IMAGE_LIST_MENU_ID]);

    const listContextMenu = createImageListContextMenu();

    appearMenu(e, listContextMenu);

}

async function removeImage(imageId) {
    return fetch(`${IMAGE_API_HOST}/${imageId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
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

function openDockerfileEditor(targetId) {

    const msg = `# Write the contents of the Dockerfile here.
# To build this Dockerfile, right-click and select the appropriate menu option.
# The Dockerfile will not be saved.
# It will be created as a temporary file and removed after the build.
FROM `;

    const mirror = CodeMirror(document.querySelector(`#${targetId}`), {
          lineNumbers: true,
          tabSize: 2,
          value: msg,
          mode: 'dockerfile'
        });
        mirror.setSize('100%','100%');
    return mirror;
}

function handleDockerfileContextEvent(e) {
    e.preventDefault();

    clearMenus([DOCKERFILE_MENU_ID]);

    const dockerfileContextMenu = createDockerfileContextMenu();

    appearMenu(e, dockerfileContextMenu);

}

function createDockerfileContextMenu() {

    const container = createMenuContainer(DOCKERFILE_MENU_ID);

    const buildBtn = createContextMenuItem('Build Dockerfile', 'div');

    buildBtn.addEventListener('click', () => {

    });

    const exitBtn = createContextMenuItem('Exit', 'a');
    exitBtn.classList.add('text-danger');
    exitBtn.href = '/dockers/images';

    container.appendChild(buildBtn);
    container.appendChild(exitBtn);

    return container;
}