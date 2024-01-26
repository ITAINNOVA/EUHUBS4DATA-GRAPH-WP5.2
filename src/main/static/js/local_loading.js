
let NEO4J_DB_PORT="7474"

/**
 * Retrieves the local IP address and updates the database view link.
 */
function getLocalIP() {
    // Get the current host from the window location
    var status = window.location.host;

    // Split the host by colon to remove any port number
    var content_status = status.split(":");
    if (content_status.length > 0) {
        // Set the status to the first part of the split host
        status = content_status[0];
    }

    // Replace the element with the updated link
    $('#load_my_local_ip').replaceWith(
        `<a class="nav-link link external" aria-current="page" href="http://${status}:${NEO4J_DB_PORT}/browser/">Database view</a>`
    );
}



$(document).ready(function () {
    getLocalIP();
});