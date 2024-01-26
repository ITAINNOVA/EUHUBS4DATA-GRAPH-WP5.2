
from __future__ import absolute_import, unicode_literals
from end_point.logging_ita import application_logger
from end_point.business.controllers.controllers import wrapper, aux_graph_visualize
from end_point.api.api_apply_match_and_map_service import config
from end_point.config import db_cache
from end_point.api.api_semantic_search_nodes_service import config

def controller_query_nodes(query_node, query_size):
    """
    Returns all the nodes related to the query provided.
    In case of working succesfully:
    {
        'json_content': Json dictionary with the Neo4j graph format.
            Neo4j graph format -> https://neo4j.com/docs/http-api/current/actions/return-results-in-graph-format/
        'graph_content': Json to create the cytoscape graph which will
        be displayed in the web interface -> https://js.cytoscape.org/
        {
            'nodes':{

            }
            'edges':{

            }

        }
    }

    In case of failure:
    {
        'error': Error message
        'codestatus': Error code
    }
    """
    graph_content = {}
    message = None
    list_graph_result = list()
    color_class = None
    json_content = None
    status_code = 200

    if query_node and (query_node != '' or query_node != ' '):
        try:
            list_uri = wrapper.search_index.search_in_index_consulting(query_node, query_size)
            list_nodes, list_edges, list_graph_result = aux_graph_visualize(list_uri, list_graph_result)

            graph_content['nodes'] = list_nodes
            graph_content['edges'] = list_edges

        except Exception as e:
            application_logger.error(f"Exception caugth: {str(e)}")
            application_logger.error(e, exc_info=True)
            status_code = 500

        color_class = db_cache.get_all_color_class()
        json_content = list_graph_result

    else:
        message = "Nothing have been written to be queried on the database"
        status_code = 400
    return color_class, json_content, graph_content, message, status_code

# -------------- TASK --------------
def controller_query_nodes_task(query_node, query_size):
    color_class, json_content, graph_content, message, status_code = controller_query_nodes(
        query_node, query_size)
    return {
        config.COLOR_CLASS: color_class,
        config.JSON_CONTENT: json_content,
        config.GRAPH_CONTENT: graph_content,
        'message': message
    }, status_code



