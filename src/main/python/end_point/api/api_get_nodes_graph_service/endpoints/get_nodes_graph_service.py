
from flask_restx import Resource

from end_point.api.restplus import api
from end_point.api.api_get_nodes_graph_service.serializers import get_nodes_fields
from end_point.api.api_get_nodes_graph_service.parsers import get_nodes_arg_json_model,get_nodes_parser
from end_point.api.api_get_nodes_graph_service import config
ns = api.namespace(config.APP_URL, description=config.GETNODE_DESC)

from end_point.business.controllers.controller_get_nodes_graph.tasks import controller_get_nodes_graph_task

@ns.route('')
class GetGetNodes(Resource):

    @ns.marshal_with(get_nodes_fields)
    @ns.expect(get_nodes_arg_json_model)
    def post(self):
        """
        This :POST request returns the database in Neo4j graph format
        """
        request_args = get_nodes_parser.parse_args()    
        return controller_get_nodes_graph_task(request_args[config.MAPPING])
    