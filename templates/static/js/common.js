const ROOT = "#root";
const API_PORT = "8000";
const API_HOST = `http://localhost:${API_PORT}/api`;

function alertErrorMsg(isReload) {
    alert('An error occurred. Please try it again.');
    if ( isReload ) {
        location.reload();
    }
}

