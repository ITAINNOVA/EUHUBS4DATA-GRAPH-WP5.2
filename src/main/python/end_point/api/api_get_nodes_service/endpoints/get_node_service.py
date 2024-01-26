
from end_point.api.api_get_nodes_service import config
from flask_restx import Resource
from end_point.api.restplus import api
from end_point.api.api_get_nodes_service.serializers import controller_get_nodes_fields
from end_point.api.api_get_nodes_service.parsers import controller_get_nodes_arg_json_model, controller_get_nodes_parser
from end_point.business.controllers.controller_get_nodes.tasks import controller_get_nodes_task
from end_point.api.api_get_nodes_service import config as settings

ns = api.namespace(settings.APP_URL, description=settings.GETNODE_DESCP)


@ns.route('')
class GetGetNodes(Resource):

    @ns.marshal_with(controller_get_nodes_fields)
    @ns.expect(controller_get_nodes_arg_json_model)
    def get(self):
        """
        Returns all the nodes related to a class from an ontology.
        Returns a json file with the nodes, in case of failure it
        just returns {}
        """
        request_args = controller_get_nodes_parser.parse_args()
        return controller_get_nodes_task(request_args[config.ONTOLOGY], request_args[config.CLASSNODE])
