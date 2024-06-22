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