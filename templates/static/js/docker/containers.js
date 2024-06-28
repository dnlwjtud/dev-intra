function changeToSpinner(targetBtnId, type) {
    const stopBtn = document.getElementById(targetBtnId);

    stopBtn.disabled = true;
    stopBtn.innerText = '';

    const spinner = createSmSpinner(type);
    stopBtn.appendChild(spinner);
}

function getContainerIdFromCurUrl() {
    const path = location.pathname.split('/');
    return path[path.length-1];
}

function ctrlContainer(containerId, ctrlType) {
    fetch(`http://localhost:8000/api/dockers/containers/${containerId}/${ctrlType}`, {
        method: "PUT"
    })
    .then(resp => {
        if (resp.status !== resp.ok) {
            let err = new Error();
            err.status = resp.status;

            return resp.json().then(body => {
                err.body = body;
                throw err;
            });
        }
        return resp.json();
    })
    .then( data => {

        if ( data.target_id === containerId ) {
            alert(data.msg);
            location.reload();
        }

    })
    .catch(
        err => {
            if ( err.body.msg ) {
                alert(err.body.msg);
            }
            location.reload();
        }
    );
}

function handleStopBtn() {

    const containerId = getContainerIdFromCurUrl();

    changeToSpinner('stop-container-btn', 'danger');
    ctrlContainer(containerId, 'stop');

}

function handleStartBtn() {

    const containerId = getContainerIdFromCurUrl();

    changeToSpinner('start-container-btn', 'success');
    ctrlContainer(containerId, 'start');

}

function handleRestartBtn() {

    const containerId = getContainerIdFromCurUrl();

    changeToSpinner('restart-container-btn', 'success');
    ctrlContainer(containerId, 'restart');

}

function openTerminal() {

    const consoleWrapper = document.getElementById('console-wrapper');

    const closeBtn = document.getElementById('exec-cls-btn');

    const terminal = createTerminal();
    consoleWrapper.appendChild(terminal);

    const lineInput = document.getElementById('terminal-input');
    lineInput.focus();

    const containerId = getContainerIdFromCurUrl();
    const socket  = new WebSocket(`ws://localhost:8000/api/dockers/containers/${containerId}/ws`);

    const terminalInput = document.getElementById('terminal-input');
    const outputContent = document.getElementById('output-content');

    let curCmd = null;

    socket.onopen = () => {
        console.log('WebSocket connection opened');
    };

    socket.onclose = () => {
        console.log('WebSocket connection closed');
    };

    socket.onmessage = (evt) => {

        const lines = evt.data.split('\n');
        lines.forEach((line) => {
            console.log('new line');
            console.log(line);
            const lineContainer = document.createElement('div');
            lineContainer.innerText = line;

            if ( curCmd ) {
                curCmd.appendChild(lineContainer);
            } else {
                outputContent.appendChild(lineContainer);
            }
        });

        outputContent.scrollTop = outputContent.scrollHeight;

    }

    terminalInput.addEventListener('keydown', (evt) => {
        if ( evt.key === 'Enter' ) {
            evt.preventDefault();

            const inputCmd= terminalInput.value;

            socket.send(inputCmd);

            terminalInput.value = '';
            terminalInput.disabled = true;

            const cmdDiv = document.createElement('div');
            cmdDiv.innerHTML = `<div><span id="prompt">$</span>${inputCmd}</div>`;
            outputContent.appendChild(cmdDiv);

            curCmd = document.createElement('div');
            cmdDiv.appendChild(curCmd);

            outputContent.scrollTop = outputContent.scrollHeight;
            terminalInput.disabled = false;

        }
    });

    closeBtn.addEventListener('click', () => {

        socket.close();
        console.log("socket was closed");

        const consoleWrapper = document.getElementById('console-wrapper');
        consoleWrapper.innerHTML = '';

    })

}


