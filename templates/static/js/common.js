const ROOT = "#root";
const API_PORT = "8000";
const API_HOST = `http://localhost:${API_PORT}/api`;

function alertErrorMsg(isReload) {
    alert('An error occurred. Please try it again.');
    if ( isReload ) {
        location.reload();
    }
}

function getValuesFromSelect(targetId) {

    const targetEl = document.getElementById(targetId);

    if (!targetEl) return null;

    return Array.from(targetEl.children).map(el => el.value);

}

function validateItemContains(origin, target) {
    return origin.filter(i => target.includes(i));
}