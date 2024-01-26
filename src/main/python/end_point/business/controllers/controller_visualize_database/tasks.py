
from __future__ import absolute_import, unicode_literals

from end_point.logging_ita import application_logger
from end_point.business.controllers.controllers import wrapper
from flask import Response
import json
from end_point.config import db_cache


def controller_visualize_database():
    try:
        # Request the whole database as a JSON graph
        json_graph = wrapper.database_conector.request_the_whole_database()

        # Create a new temporary class for color caching
        db_cache.new_tmp_class_color()

        # Map the JSON graph to a Cytoscape graph
        cytoscape_graph = wrapper.map_to_cytospace(json_graph)

        # Get all color classes from the cache
        list_color_class = db_cache.get_all_color_class()

        # Create a dictionary with the Cytoscape graph and color classes
        result_dict = {
            'cytoscape_graph': cytoscape_graph,
            'color_class': list_color_class
        }

        # Return the dictionary and a status code of 202 (Accepted)
        return result_dict, 202

    except Exception as e:
        # Log the exception
        application_logger.error(f"Exception caught: {str(e)}")
        application_logger.error(e, exc_info=True)

        # Return a JSON response with the error message and status code 500 (Server Error)
        return Response(json.dumps({"error": "Server error, it has crashed", "codestatus": 500, "exception": str(e)}), 500, mimetype='application/json')

