/**
 * Load ontology data and populate dropdown selectors.
 */
function loadOntology() {
    // Fetch locations data and append options to the country selector
    $.get("/_find_locations", function (data, status) {
        // Use template to generate option elements and append to selector
        $.tmpl('<option value=${key} id=${key}> ${name}</option>', data).appendTo('#country-dataset-selector');
    })

    // Fetch domains data and append options to the domain selector
    $.get("/_find_domains", function (data, status) {
        // Use template to generate option elements and append to selector
        $.tmpl('<option value=${key} id=${key}> ${name}</option>', data).appendTo('#domain-dataset-selector');
    })
}


$(document).ready(function () {
    loadOntology();
});