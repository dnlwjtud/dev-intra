function handleStopBtn() {

    const path = location.pathname.split('/');
    const containerId = path[path.length-1];

    const stopBtn = document.getElementById('stop-container-btn');

    stopBtn.disabled = true;
    stopBtn.innerText = '';

    const spinner = createSmSpinner('danger');
    stopBtn.appendChild(spinner);

    fetch(`http://localhost:8000/api/dockers/containers/${containerId}`, {
        method: "PATCH"
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
            alert('container was successfully stopped.');
            location.reload();
        }

    })
    .catch(
        err => {
            if ( err.body.msg ) {
                alert(err.body.msg);
            }
            location.reload();
            return;
        }
    )

}