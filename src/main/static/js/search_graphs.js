function show_graph(data) {
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
                        'height': function (ele) { return ele.data('size_node') },
                        'width': function (ele) { return ele.data('size_node') },
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

}


/**
 * Requests the database graph from the API and displays it
 */
function request_and_display_database_graph() {
    // Show loading popup
    $('#popup').fadeIn('slow');
    $("#popup-container-id").addClass("loading");

    // Send AJAX request to get the database graph
    $.ajax({
        url: '/api/database_graph',
        type: "get",
        success: function (query_result) {
            let data = query_result.cytoscape_graph;
            // Display the graph
            show_graph(data);
            // Hide the popup
            $('#popup').fadeOut('slow');
            // Update the color legend
            let map_color_class = query_result.color_class;
            $('#list_color_legend').empty();
            $('<li class="list-group-item"> <h2>Color - Class</h2></li>').appendTo('#list_color_legend');
            $.tmpl('<li class="list-group-item"><button type="button" class="btn btn-primary" style="background-color: ${color};"></button><span> ${classe}</span></li>', map_color_class).appendTo('#list_color_legend');

        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
            // Display error popup
            error_popup(jqXHR.responseJSON.error);
        }
    });
}

/**
 * Show an error popup with the given error message.
 * @param {string} error - The error message to display.
 */
function error_popup(error){
    // Show the popup
    $('#popup').fadeIn('slow');
    // Set the title of the error message
    $("#mapping_id_element").html('<h2 class="card-title" id="mapping_id_element">Error while building graph</h2>');
    // Set the error message content
    $('#list_color_popup').html('<div class="card center" style="width: 18rem;"><div class="card-body"><h5 class="card-title">Error Message</h5><p class="card-text">'+error+'</p></div><a href="/" class="btn btn-danger">Go back</a></div>');
}


//Adding Pop up boxes to cytoscape
// https://github.com/cytoscape/ipycytoscape/issues/82
$(document).ready(function () {

    $("#display-cy-id-div").remove();

});