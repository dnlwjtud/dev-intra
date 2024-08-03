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

function handleAppendPortEvent() {

    const protocolEl = document.getElementById('network-protocol-sel');
    const portListEl = document.getElementById('port-list');

    const hostPortEl = document.getElementById('host-port');
    const guestPortEl = document.getElementById('guest-port');

    const protocol = protocolEl.selectedOptions[0].value;
    const hostPort = hostPortEl.value.trim();
    let guestPort = guestPortEl.value.trim();

    if ( !hostPort.match(/^\d+$/) ) {
        alert('Host port must be a number');
        return;
    }

    if ( !guestPort.match(/^[0-9\s]+$/) ) {
        alert('Guest port must be numbers or spaces');
        return;
    }

    const portListItems = getValuesFromSelect('port-list');

    const listHostPorts = portListItems.map( i => i.split('->')[0].trim().split('/')[0].trim());

    if ( listHostPorts.includes(hostPort) ) {
        alert('This port was already appended. Please check it again.');
        return;
    }

    const listGuestPorts = portListItems.map( i => JSON.parse(i.split('->')[1].trim()));

    const guestPortsArray = guestPort.split(' ').map(i=>i.trim());

    const hasDuplicate = listGuestPorts.some(ports => guestPortsArray.some(port => ports.includes(parseInt(port))));

    if ( hasDuplicate ) {
        alert('Some port was duplicated. Please check it again.');
        return;
    }

    guestPort = new Set(guestPort.split(' ').map(i => parseInt(i)));
    const portDesc = `${hostPort}/${protocol} -> ${JSON.stringify(Array.from(guestPort))}`;

    const portOption = document.createElement('option');
    portOption.value = portDesc;
    portOption.innerText = portDesc;

    portListEl.appendChild(portOption);

    hostPortEl.value = '';
    guestPortEl.value = '';

}

function handleAppendEnvVar() {

    const envVarListEl = document.getElementById('env-var-list');

    const envVarKeyEl = document.getElementById('env-var-key');
    const envVarValueEl = document.getElementById('env-var-value');

    const envKey = envVarKeyEl.value.trim();
    const envValue = envVarValueEl.value.trim();

    if (!envKey) {
        alert('Key is must to be input.');
        return;
    }

    if (!envValue) {
        alert('Value is must to be input.');
        return;
    }

    const listEnvValues = getValuesFromSelect('env-var-list');

    const listKeys = listEnvValues.map(i => i.split('=')[0]);
    const listValues = listEnvValues.map(i => i.split('=')[1]);

    if ( listKeys.includes(envKey) || listValues.includes(envValue) ) {
        alert('There is duplicated key or value. Please check it again.');
        return;
    }

    const envDesc = `${envKey}=${envValue}`;
    const envOption = document.createElement('option');
    envOption.value = envDesc;
    envOption.innerText = envDesc;

    envVarListEl.appendChild(envOption);

    envVarKeyEl.value = '';
    envVarValueEl.value = '';

}

function removeModal(modalId) {
    const modalEl = document.getElementById(modalId);
    modalEl.remove();
}

function runContainer() {

    const image = document.getElementById('image-id').selectedOptions[0].value;
    const network = document.getElementById('network-id').selectedOptions[0].value;
    const name = document.getElementById('name').value;
    const ports = {};
    const environment = getValuesFromSelect('env-var-list');
    const command = document.getElementById('cmd').value;

    const portList = getValuesFromSelect('port-list');
    portList.forEach( port => {
        const portSplit = port.split('->');
        const hostPort = portSplit[0].trim();
        ports[hostPort] = JSON.parse(portSplit[1]);
    });

    const data = {
        image,
        network,
        name,
        ports,
        environment,
        command
    };

    const runBtn = document.getElementById('run-btn');
    const cancelBtn = document.getElementById('cancel-btn');

    runBtn.disabled = true;
    cancelBtn.disabled = true;

    fetch(`${CONTAINER_API_HOST}/run`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    }).then(
        resp => {
            if ( resp.status >= 400 ) {
                alert('an error occurred.');
                location.reload();
            } else {
                return resp.json();
            }
        }
    ).then(
        data => {
            alert(data.msg);
            location.replace('/');
        }
    );

}

