from flask_restx import fields
from end_point.api.restplus import api
from end_point.api.api_get_nodes_service import config

controller_get_nodes_fields = api.model('GetNodes', {
    config.GET_NODE_DICT_NODE: fields.Raw(required=True, description=config.NODE_DICT_DESCRIPTION),    
    "message": fields.String(required=True)
    })
