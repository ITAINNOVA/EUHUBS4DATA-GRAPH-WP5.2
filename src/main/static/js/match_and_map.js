//Adding Pop up boxes to cytoscape
async function sleep(milli_seconds = 1000) {return new Promise(done => setTimeout(() => done(), milli_seconds));}
/**
 * Loads the graph map based on the provided URI list.
 * https://github.com/cytoscape/ipycytoscape/issues/82
 * @param {Array} uri_list - The list of URIs for mapping.
 */
async function load_graph_map(uri_list) {
    let dataset_query = { 'mapping': uri_list }
    console.log(JSON.stringify(dataset_query))
    $.ajax({
        url: '/api/get_nodes_graph',
        type: "post",
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(dataset_query),
        success: async function (data_content) {
            console.log(data_content.message);

            if (data_content !== null) {
                let data = data_content.cytoscape_graph
                var cy = cytoscape(
                    {
                        container: $('#cy'),
                        wheelSensitivity: 0.2,
                        // Nodes and edges are in a separate file for easier creation with external programming language.
                        elements: data,
                        layout: {
                            name: 'cose-bilkent',

                            // Called on `layoutready`
                            ready: function () {
                            },
                            // Called on `layoutstop`
                            stop: function () {
                            },
                            // 'draft', 'default' or 'proof" 
                            // - 'draft' fast cooling rate 
                            // - 'default' moderate cooling rate 
                            // - "proof" slow cooling rate
                            quality: 'default',
                            // Whether to include labels in node dimensions. Useful for avoiding label overlap
                            nodeDimensionsIncludeLabels: false,
                            // number of ticks per frame; higher is faster but more jerky
                            refresh: 30,
                            // Whether to fit the network view after when done
                            fit: true,
                            // Padding on fit
                            padding: 10,
                            // Whether to enable incremental mode
                            randomize: true,
                            // Node repulsion (non overlapping) multiplier
                            nodeRepulsion: 5000,
                            // Ideal (intra-graph) edge length
                            idealEdgeLength: 500,
                            // Divisor to compute edge forces
                            edgeElasticity: 0.45,
                            // Nesting factor (multiplier) to compute ideal edge length for inter-graph edges
                            nestingFactor: 0.1,
                            // Gravity force (constant)
                            gravity: 0.25,
                            // Maximum number of iterations to perform
                            numIter: 2500,
                            // Whether to tile disconnected nodes
                            tile: true,
                            // Type of layout animation. The option set is {'during', 'end', false}
                            animate: 'end',
                            // Duration for animate:end
                            animationDuration: 500,
                            // Amount of vertical space to put between degree zero nodes during tiling (can also be a function)
                            tilingPaddingVertical: 10,
                            // Amount of horizontal space to put between degree zero nodes during tiling (can also be a function)
                            tilingPaddingHorizontal: 10,
                            // Gravity range (constant) for compounds
                            gravityRangeCompound: 1.5,
                            // Gravity force (constant) for compounds
                            gravityCompound: 1.0,
                            // Gravity range (constant)
                            gravityRange: 3.8,
                            // Initial cooling factor for incremental layout
                            initialEnergyOnIncremental: 0.5
                        },
                        selectionType: "additive",
                        panningEnabled: true,
                        zoomingEnabled: true,
                        // so we can see the ids
                        style: [
                            {
                                selector: 'node',
                                style: {
                                    'height': 80,
                                    'width': 80,
                                    'label': 'data(label)',
                                    'background-fit': 'contain',
                                    'background-clip': 'none',
                                    'text-wrap': 'wrap',
                                    'text-halign': 'center',
                                    'text-valign': 'center',
                                    'background-color': function (ele) { return ele.data('colorid'); },
                                }
                            }, {
                                selector: 'edge',
                                style: {
                                    'text-wrap': 'wrap',
                                    'label': 'data(label)',
                                    'text-background-color': 'yellow',
                                    'text-background-opacity': 0.4,
                                    'width': '6px',
                                    'target-arrow-shape': 'triangle',
                                    'control-point-step-size': '140px',
                                    'curve-style': 'bezier'
                                }
                            },
                            {
                                selector: 'node',
                                css: {
                                    'text-valign': 'center',
                                    'color': 'white',
                                    'text-outline-width': 2,
                                }
                            },
                            {
                                selector: ':selected',
                                css: {
                                    'background-color': 'black',
                                    'line-color': 'black',
                                    'target-arrow-color': 'black',
                                    'source-arrow-color': 'black',
                                    'text-outline-color': 'black'
                                }
                            }
                        ],
                    }
                );

                cy.elements().qtip({
                    content: function () { return this.data('attributes'); },
                    position: {
                        my: 'top center',
                        at: 'bottom center'
                    },
                    style: {
                        tip: {
                            width: 16,
                            height: 8
                        }
                    }
                });

                let map_color_class = data_content.color_class
                $('#list_color_legend').empty()
                $('<li class="list-group-item"> <h2>Color - Class</h2></li>').appendTo('#list_color_legend');
                $.tmpl('<li class="list-group-item"><button type="button" class="btn btn-primary" style="background-color: ${color};" ></button><span> ${classe}</span></li>', map_color_class).appendTo('#list_color_legend');

            }
        },
        error: function (xhr, status, error) {
            displayErrorPopup(xhr, error, status);
        }
    });

}

/**
 * Updates the popup with new data.
 *
 * @param {Array} data - The data to update the popup with.
 */
function update_popup(data) {
    // Update the mapping ID element with a loading message
    $("#mapping_id_element").html('<h2 class="card-title" id="mapping_id_element">Mapping datasets...</h2>');
    // Fade in the popup
    $('#popup').fadeIn('slow');
    // Append list items to the color popup list
    $.tmpl('<li class="list-group-item"><span> ${dataset_name}</span></li>', data).appendTo('#list_color_popup');
    // Add the "loading" class to the popup container
    $("#popup-container-id").addClass("loading");
}

/**
 * Display an error popup with the provided XHR, status, and error information.
 * The popup will fade in slowly and show an error message along with a "Go back" button.
 * @param {XMLHttpRequest} xhr - The XMLHttpRequest object.
 * @param {string} status - The status of the request.
 * @param {string} error - The error message.
 */
function displayErrorPopup(xhr, status, error) {
    // Fade in the popup element
    $('#popup').fadeIn('slow');

    // Update the content of the mapping_id_element with the error message
    $("#mapping_id_element").html('<h2 class="card-title" id="mapping_id_element">Error while requesting datasets</h2>');

    // Clear the list_color_popup element and populate it with the error message and a "Go back" button
    $('#list_color_popup').empty().html(`
        <div class="p-2 row" id="fill_later_with_url">
            <div class="p-3 card" style="width: 18rem;">
                <div class="card-body">
                    <h5 class="card-title">Error occurred while analyzing</h5>
                    <p class="card-text"><strong>Status</strong>: ${status}.</p>
                    <p class="card-text"><strong>Error</strong>: ${error}.</p>
                    <a href="/" class="btn btn-danger">Go back</a>
                </div>
            </div>
        </div>`
    );
}


/**
 * Show a loading spinner and message while processing data.
 */
function loadSpinner() {
    // Show the popup
    $('#popup').fadeIn('slow');

    // Replace the mapping id element with the loading spinner and message
    $('#mapping_id_element').replaceWith(`
        <div class="p-2 row" id="fill_later_with_url">
            <div class="p-3 container">
                <h2>Processing your data...</h2>
                <p>Your submitted file is being analyzed, this process can last long, please wait until it is completed.</p>
                <div class="spinner-grow" style="width: 3rem; height: 3rem;" role="status"></div>
                <div class="spinner-grow" style="width: 3rem; height: 3rem;" role="status"></div>
                <div class="spinner-grow" style="width: 3rem; height: 3rem;" role="status"></div>
                <div class="spinner-grow" style="width: 3rem; height: 3rem;" role="status"></div>
            </div>
        </div>`
    );

    // Add the loading class to the popup container
    $("#popup-container-id").addClass("loading");
}


$(document).ready(function () {

    $("#match_and_map_form").submit(function (event) {
        // Prevent the page from reloading
        event.preventDefault();
        // Set the text-output span to the value of the first input
        //text-to-graph
        let $input = $(this).find('#text-to-graph');

        let dataset_query = {
            textarea: $input.val()
        }
        loadSpinner();
        $.ajax({
            url: "/api/apply_match_and_map",
            type: "post",
            data: JSON.stringify(dataset_query),
            dataType: 'json',
            contentType: 'application/json',
            success: async function (data_content) {
                console.log(data_content.message);
                if (data_content !== null) {
                    $("#popup-container-id").removeClass("loading");
                    $('#popup').fadeOut('slow');
                    await load_graph_map(data_content.uri_list);
                }
            },
            error: function (xhr, status, error) {
                displayErrorPopup(xhr, error, status);
            }

        });

    });
    $("#map_metadata_form").submit(async function (event) {
        // Prevent the page from reloading
        event.preventDefault();

        // let $input = $(this).find('#name-dataset-graph');
        //let $description = $(this).find('#description-dataset-graph');
        //let $country = $(this).find('#country-dataset-selector');
        //let $domain = $(this).find('#domain-dataset-selector');
        //let dataset_query = {
        //    "name": $input.val(),
        //    "location": $country.val(),
        //    "description": $description.val(),
        //    "domains": $domain.val()
        //}
        let dataset_query = {

        }
        loadSpinner();

        $.ajax({
            url: "/api/request_joyce_metadata",
            type: "post",
            data: JSON.stringify(dataset_query),
            dataType: 'json',
            contentType: 'application/json',
            success:  async function (data_content) {

                update_popup(data_content.uri_list)

                if (data_content !== null) {
                    $.ajax({
                        url: "/api/map_joyce2_metadata",
                        type: "post",
                        data: JSON.stringify(dataset_query),
                        dataType: 'json',
                        contentType: 'application/json',
                        success:  async function (data_content) {
                            console.log(data_content.message);
                            if (data_content !== null) {
                                $("#popup-container-id").removeClass("loading");
                                $('#popup').fadeOut('slow');
                                await load_graph_map(data_content.uri_list);
                            }

                        },
                        error: function (xhr, status, error) {
                            displayErrorPopup(xhr, error, status);
                        }
                    });

                }

            },
            error: function (xhr, status, error) {
                displayErrorPopup(xhr, error, status);;
            }

        });

    });

});

