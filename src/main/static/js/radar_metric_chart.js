//ids//base
async function sleep(milli_seconds = 1000) {return new Promise(done => setTimeout(() => done(), milli_seconds));}
const labels = ["LCOMOnto", "WMCOnto2", "DITOnto", "NACOnto", "NOCOnto", "CBOOnto", "RFCOnto", "NOMOnto", "RROnto", "PROnto", "AROnto", "INROnto", "ANOnto", "TMOnto2"];

/**
 * Builds a table with the given data and appends it to the specified element.
 *
 * @param {Object} json_base - The base JSON data.
 * @param {Object} json_ids - The JSON data containing IDS.
 * @param {string} table_id - The ID of the element where the table will be appended.
 */
function build_table(json_base, json_ids, table_id) {
    // Create the table element
    var table = document.createElement('table');
    
    // Create the table header
    var thead = document.createElement('thead');
    var tr = document.createElement('tr');

    // Create the table header cells
    var th0 = document.createElement('th');
    var th1 = document.createElement('th');
    var th2 = document.createElement('th');

    // Create the text nodes for the table header cells
    var text0 = document.createTextNode('Metric');
    var text1 = document.createTextNode('IDS base');
    var text2 = document.createTextNode('IDS populated');

    // Append the text nodes to the table header cells
    th0.appendChild(text0);
    th1.appendChild(text1);
    th2.appendChild(text2);

    // Append the table header cells to the table row
    tr.appendChild(th0);
    tr.appendChild(th1);
    tr.appendChild(th2);

    // Append the table row to the table header
    thead.appendChild(tr);
    
    // Append the table header to the table
    table.appendChild(thead);

    // Create the table body
    var tbody = document.createElement('tbody');

    // Set the class name for the table
    table.className = "table table-hover table-striped";

    // Iterate over the base JSON data and create table rows
    for (const [key, value] of Object.entries(json_base)) {
        tr = document.createElement('tr');

        // Create the table cells
        var td1 = document.createElement('td');
        var td2 = document.createElement('td');
        var td3 = document.createElement('td');

        // Create the text nodes for the table cells
        var text1 = document.createTextNode(key);
        var text2 = document.createTextNode(value);
        var text3 = document.createTextNode(json_ids[key]);

        // Append the text nodes to the table cells
        td1.appendChild(text1);
        td2.appendChild(text2);
        td3.appendChild(text3);

        // Append the table cells to the table row
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);

        // Append the table row to the table body
        tbody.appendChild(tr);
    }

    // Append the table body to the table
    table.appendChild(tbody);

    // Append the table to the specified element
    $(table_id).append(table);
}



/**
 * Requests the ontology metrics from the API and updates the DOM with the metrics data.
 */
function request_metrics() {
  // HTML content for when no metrics are available
  var notfoundcontent = `
    <div class="py-2 container" id="notfound">
        <div class="notfound">
            <div class="notfound-404">
                <h3>Oops! No available metrics</h3>
                    <h1><span>4</span><span>0</span><span>4</span></h1>
            </div>
            <h2>we are sorry,but we could found the metrics of the ontology</h2>
        </div>
    </div>
  `;

  // Make AJAX request to get the ontology metrics
  $.ajax({
    url: '/api/ontology_metrics_array',
    type: "get",
    success: function (data) {
      let data_content = data.metrics;
      let data_message = data.message;

      if (data_content !== null) {
        let metrics_result = data_content;
        let result = data_message.includes("error");

        if (result) {
          // Display the not found content
          $('#id_metrics_container').html(notfoundcontent);
        } else {
          // Populate the tables with the metrics data
          build_table(metrics_result['base']['values'], metrics_result['ids']['values'], "#id_quore_values");
          build_table(metrics_result['base']['scores'], metrics_result['ids']['scores'], "#id_quore_scores");
          build_table(metrics_result['base']['oquare_structural'], metrics_result['ids']['oquare_structural'], "#id_structural");
          build_table(metrics_result['base']['oquare_operability'], metrics_result['ids']['oquare_operability'], "#id_operability");
          build_table(metrics_result['base']['oquare_reliability'], metrics_result['ids']['oquare_reliability'], "#id_reliability");
          build_table(metrics_result['base']['oquare_transferability'], metrics_result['ids']['oquare_transferability'], "#id_transferability");
          build_table(metrics_result['base']['oquare_adequacy'], metrics_result['ids']['oquare_adequacy'], "#id_adequacy");
          build_table(metrics_result['base']['oquare_maintainbility'], metrics_result['ids']['oquare_maintainbility'], "#id_maintainability");
          build_table(metrics_result['base']['oquare_compatibility'], metrics_result['ids']['oquare_compatibility'], "#id_compatibility");

          // Display the radar and bar charts with the metrics data
          display_radar_chart_metrics(metrics_result['base']['value_list'], metrics_result['ids']['value_list']);
          display_bar_chart_metrics(metrics_result['base']['score_list'], metrics_result['ids']['score_list']);
        }
      }
    },
    error: function (jqXHR, textStatus, errorThrown) {
      console.log(textStatus, errorThrown);
      // Display the not found content in case of an error
      $('#id_metrics_container').html(notfoundcontent);
    }
  });
}


/**
 * Display a radar chart with metrics.
 * 
 * @param {number[]} ids_base_scores - The base scores for IDS ontology.
 * @param {number[]} ids_scores - The modified scores for IDS ontology.
 */
function display_radar_chart_metrics(ids_base_scores, ids_scores) {

    // Create a new radar chart instance
    const myChart = new Chart("my_Chart_radar", {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'IDS Base Ontology',
                    data: ids_base_scores,
                    borderColor: '#696969',
                    backgroundColor: '#528ff5',
                },
                {
                    label: 'IDS Modified Ontology',
                    data: ids_scores,
                    borderColor: '#696969',
                    backgroundColor: '#cc1111',
                },
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Chart.js Radar Chart'
                }
            }
        },
    });

}

/**
 * Display bar chart metrics.
 * @param {number[]} ids_base_scores - Array of IDS base scores.
 * @param {number[]} ids_scores - Array of IDS modified scores.
 */
function display_bar_chart_metrics(ids_base_scores, ids_scores) {
    // Create a new Chart instance
    const myChart = new Chart("my_Chart_bar", {
        type: 'bar', // Set the chart type to bar
        data: {
            labels: labels, // Set the labels for the chart
            datasets: [
                {
                    label: 'IDS Base Ontology', // Set the label for the first dataset
                    data: ids_base_scores, // Set the data for the first dataset
                    borderColor: '#696969', // Set the border color for the first dataset
                    backgroundColor: '#528ff5', // Set the background color for the first dataset
                    borderWidth: 2, // Set the border width for the first dataset
                    borderRadius: 5, // Set the border radius for the first dataset
                    borderSkipped: false, // Set the border skipped for the first dataset
                },
                {
                    label: 'IDS Modified Ontology', // Set the label for the second dataset
                    data: ids_scores, // Set the data for the second dataset
                    borderColor: '#696969', // Set the border color for the second dataset
                    backgroundColor: '#cc1111', // Set the background color for the second dataset
                    borderWidth: 2, // Set the border width for the second dataset
                    borderRadius: 5, // Set the border radius for the second dataset
                    borderSkipped: false, // Set the border skipped for the second dataset
                },
            ]
        },
        options: {
            responsive: true, // Make the chart responsive
            plugins: {
                legend: {
                    position: 'top', // Set the position of the legend to top
                },
                title: {
                    display: true,
                    text: 'Chart.js Bar Chart' // Set the title for the chart
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Value' // Set the title for the y-axis
                    },
                    suggestedMin: 0, // Set the suggested minimum value for the y-axis
                    suggestedMax: 5 // Set the suggested maximum value for the y-axis
                }
            }
        },
    });

}



$(document).ready(function () {
    $("#display-cy-id-div").remove();
    request_metrics();
});

