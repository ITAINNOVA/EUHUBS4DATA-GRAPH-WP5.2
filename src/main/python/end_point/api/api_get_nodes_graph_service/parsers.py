from flask_restx import fields, reqparse
from end_point.api.restplus import api
from end_point.api.api_get_nodes_graph_service import config

get_nodes_arg_json_model = api.model(
    "GetNodesRequest",
    {
        config.MAPPING: fields.List(fields.String(),required=True, description=config.MAPPING_DESC),
    },
)

get_nodes_parser = reqparse.RequestParser()
get_nodes_parser.add_argument(config.MAPPING, required=True, help=config.MAPPING_DESC,location='json',type=list)
