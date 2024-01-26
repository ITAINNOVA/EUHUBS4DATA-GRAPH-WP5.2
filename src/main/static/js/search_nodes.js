async function sleep(milli_seconds = 1000) {return new Promise(done => setTimeout(() => done(), milli_seconds));}
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
 * Requests and displays a node graph.
 */
function request_and_display_node_graph() {
    // Get the status from the URL
    var status = window.location.href;
    var content_status = status.split("#");

    status = "";
    if (content_status.length > 1) {
        status = content_status[1];
        status = "http://www.w3.org/ns/dcat#" + status;

        let uri_list = [status];
        let dataset_query = { 'mapping': uri_list };

        $.ajax({
            url: '/api/get_nodes_graph',
            type: "post",
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(dataset_query),
            success: async function (query_result) {
                console.log(query_result);
                // Check if query_result is not null
                if (query_result !== null) {
                    let data = query_result.cytoscape_graph;
                    show_graph(data);
                    let map_color_class = query_result.color_class;
                    $('#list_color_legend').empty();
                    $('<li class="list-group-item"> <h2>Color - Class</h2></li>').appendTo('#list_color_legend');
                    $.tmpl('<li class="list-group-item"><button type="button" class="btn btn-primary" style="background-color: ${color};" ></button><span> ${classe}</span></li>', map_color_class).appendTo('#list_color_legend');
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        });
    } else {
        console.log("It is on the semantic search page...");
    }
}


//Adding Pop up boxes to cytoscape
// https://github.com/cytoscape/ipycytoscape/issues/82
$(document).ready(function () {

    request_and_display_node_graph();
    $("#search-id-form-advanced").submit(function (event) {
        // Prevent the page from reloading
        event.preventDefault();
        // Set the text-output span to the value of the first input
        let $input = $(this).find('#search-dataset-id');
        let $number_input = $(this).find('#id-size-nodes-to-search');
        let dataset_query = {
            consult: $input.val(),
            query_size:$number_input.val()
        }
        $.ajax({
            url: '/api/semantic_search_node',
            type: "get",
            data: dataset_query,
            success: async function (data_content) {
                console.log(data_content.message);

                if (data_content !== null){
                    show_graph(data_content.graph_content);
                    let map_color_class = data_content.color_class;
                   
                    $('#list_color_legend').empty()
                    $('<li class="list-group-item"> <h2>Color - Class</h2></li>').appendTo('#list_color_legend');
                    $.tmpl('<li class="list-group-item"><button type="button" class="btn btn-primary" style="background-color: ${color};" ></button><span> ${classe}</span></li>', map_color_class).appendTo('#list_color_legend');

                }
                
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        });
    });
});