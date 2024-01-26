from __future__ import absolute_import, unicode_literals

from end_point.logging_ita import application_logger
from end_point.business.controllers.controllers import wrapper
from end_point.config import db_cache
from end_point.api.api_get_nodes_graph_service import config

def controller_get_nodes_graph(mapping):
    """
    Returns a json dictionary with the Neo4j graph format:
    Neo4j graph format: https://neo4j.com/docs/http-api/current/actions/return-results-in-graph-format/
    In case of failure:
            {
                'error': Error message
                'codestatus': Error code
            }
    """
    cytoscape_graph = dict()
    list_color_class = list()
    message = None
    status_code = 200

    try:
        if mapping:
            json_graph = wrapper.database_conector.extract_all_nodes_as_graph(
                mapping)
            db_cache.new_tmp_class_color()
            cytoscape_graph = wrapper.map_to_cytospace(json_graph,size_score=13)
            list_color_class = db_cache.get_all_color_class()
        else:
            message = "No nodes provided for mapping"
            application_logger.error(message)
            status_code = 400

    except Exception as e:
        message = f"Server error, it has crashed Exception caugth: {str(e)}"
        application_logger.error(e, exc_info=True)
        application_logger.error(message)
        status_code = 500
    application_logger.warning(cytoscape_graph)
    application_logger.warning(list_color_class)
    application_logger.warning(message)

    return cytoscape_graph, list_color_class, message, status_code


def controller_get_nodes_graph_task(mapping):

    cytoscape_graph, list_color_class, message,status_code = controller_get_nodes_graph(mapping) 
    return {str(config.CYTOGRAPH): cytoscape_graph, str(config.COLOR_LIST): list_color_class, 'message': message}, status_code
