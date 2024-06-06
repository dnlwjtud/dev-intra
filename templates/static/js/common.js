
function appendAlert(type, msg){
    const pos = document.getElementById('alert-pos');

    if (pos.hasChildNodes()) {
        pos.innerHTML = '';
    }

    const alertDiv = document.createElement('div');

    switch (type) {
        case 'info':
            alertDiv.className = 'alert alert-primary';
            break;
        case 'success':
            alertDiv.className = 'alert alert-success';
            break;
        case 'error':
            alertDiv.className = 'alert alert-danger';
            break;
        case 'warn':
            alertDiv.className = 'alert alert-warning';
            break;
        default:
            alertDiv.className = 'alert alert-secondary';
            break;
    }

    alertDiv.innerText = msg;

    pos.appendChild(alertDiv);

}

function search_container(containerId) {

    const tr = document.getElementById(containerId);
    console.log(containerId);

    fetch(`http://localhost:8000/api/dockers/${containerId}`)
        .then(resp => resp.json())
        .then(data => {
            console.log(data);
            const { container_id, container_name, ports, is_available } = data;

            tr.children[0].innerHTML = container_id;
            tr.children[1].innerHTML = container_name;
            tr.children[2].innerHTML = ports;

            const statusTd = tr.children[3];
            statusTd.innerHTML = '';

            const statusSpan = document.createElement('span')
            statusSpan.className = `badge`;
            statusSpan.textContent = is_available ? '🟢' : '🔴';
            statusTd.appendChild(statusSpan);

            appendAlert('success', 'Container status was successfully refreshed')

        })
        .catch(err => console(err));

}