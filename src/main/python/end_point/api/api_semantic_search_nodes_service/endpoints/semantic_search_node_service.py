
from flask_restx import Resource
from end_point.api.restplus import api
from end_point.api.api_semantic_search_nodes_service.serializers import semantic_search_fields 
from end_point.api.api_semantic_search_nodes_service.parsers import semantic_search_arg_json_model,semantic_search_parser
from end_point.api.api_semantic_search_nodes_service import config
from end_point.business.controllers.controller_query_nodes.tasks import controller_query_nodes_task

ns = api.namespace(config.APP_URL, description=config.SEMANTIC_NODE_DESC)

@ns.route('')
class GetSemanticSearch(Resource):
    
    @ns.marshal_with(semantic_search_fields)
    def get(self):
        """
        Returns all the nodes related to the query provided.
        Returns two json dictionaries in two different formats.
        Json dictionary with the Neo4j graph format Json to create the cytoscape (https://js.cytoscape.org/) graph which will be displayed in the web interface.
        Returns the json dictionaries which contains the two json dictionaries.
        """
        request_args = semantic_search_parser.parse_args() 
        return controller_query_nodes_task(request_args[config.QUERY_NODE],request_args[config.QUERY_SIZE])