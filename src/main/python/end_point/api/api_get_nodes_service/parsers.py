from flask_restx import fields, reqparse

from end_point.api.restplus import api
from end_point.api.api_get_nodes_service import config

controller_get_nodes_arg_json_model = api.model(
    "GetNodesRequest",
    {
        config.ONTOLOGY: fields.String(required=True, description=config.ONTOLOGY_DESCP),
        config.CLASSNODE: fields.String(required=False, description=config.CLASSNODE_DESCP),
    },
)

controller_get_nodes_parser = reqparse.RequestParser()
controller_get_nodes_parser.add_argument(config.ONTOLOGY, required=True, help=config.ONTOLOGY_DESCP, type=str)
controller_get_nodes_parser.add_argument(config.CLASSNODE, required=True, help=config.CLASSNODE_DESCP, type=str)
