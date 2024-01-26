from flask_restx import fields, reqparse
from end_point.api.restplus import api
from end_point.api.api_semantic_search_nodes_service import config


semantic_search_arg_json_model = api.model(
    "SemanticSearchRequest",
    {
        config.QUERY_NODE: fields.String(required=True, description=config.QUERY_NODE_DESC),
        config.QUERY_SIZE: fields.String(required=True, description=config.QUERY_SIZE_DESC)
    },
)


semantic_search_parser = reqparse.RequestParser()
semantic_search_parser.add_argument(config.QUERY_NODE, required=True, help=config.QUERY_NODE_DESC, type=str, location='args')
semantic_search_parser.add_argument(config.QUERY_SIZE, required=True, help=config.QUERY_SIZE_DESC, type=str, location='args')
