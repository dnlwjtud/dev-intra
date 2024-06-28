
function appendAlert(type, msg){
    console.log("called")
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

    fetch(`http://localhost:8000/api/dockers/containers/${containerId}`)
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


function createToast(msg, type) {

    const body = document.createElement('div');

    body.classList.add('toast');
    body.setAttribute('role', 'alert');
    body.setAttribute('aria-live', 'assertive');
    body.setAttribute('aria-atomic', true);

    const header = document.createElement('div');
    header.classList.add('toast-header');

    const headerTitle = document.createElement('strong');
    headerTitle.classList.add('me-auto');
    headerTitle.innerText = "DevIntra";

    const badge = document.createElement('small');
    badge.classList.add('badge', `text-bg-${type}`);
    badge.innerText = type;

    const headerBtn = document.createElement('button');
    headerBtn.classList.add('btn-close');
    headerBtn.setAttribute('data-bs-dismiss', 'toast');
    headerBtn.setAttribute('aria-label', 'Close');

    header.appendChild(headerTitle);
    header.appendChild(badge);
    header.appendChild(headerBtn);

    const contents = document.createElement('div')
    contents.classList.add('toast-body');

    contents.innerText = msg;

    body.appendChild(header);
    body.appendChild(contents);

    return body;

}

function createSmSpinner(type) {
    const spinner = document.createElement('div');

    spinner.classList.add(
        'spinner-border',
        'spinner-border-sm',
        `text-${type}`
    );

    return spinner;
}

function createLoadingCircleBtn() {

    const btn = document.createElement('button');
    btn.classList.add('btn', 'btn-primary');

    const spinner = createSmSpinner('');
    btn.appendChild(spinner);

    return btn;

}

function createTerminal() {

    const terminal = document.createElement('div');
    terminal.id = 'terminal-body';

    const terminalWindow = document.createElement('div');
    terminalWindow.id = 'terminal-window';

    terminal.appendChild(terminalWindow);

    const terminalOutput = document.createElement('div');
    terminalOutput.id = 'terminal-output'

    terminalWindow.appendChild(terminalOutput);

    const outputContent = document.createElement('div');
    outputContent.id = 'output-content';

    const inputLine = document.createElement('div');
    inputLine.id = 'input-line';

    const prompt = document.createElement('span');
    prompt.id = 'prompt';
    prompt.innerText = '$';

    const terminalInput = document.createElement('input');
    terminalInput.id = 'terminal-input';
    terminalInput.setAttribute("autofocus","");

    inputLine.appendChild(prompt);
    inputLine.appendChild(terminalInput);

    terminalOutput.appendChild(outputContent);
    terminalOutput.appendChild(inputLine);

    return terminal;

}
