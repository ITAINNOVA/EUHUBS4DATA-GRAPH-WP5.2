from flask_restx import fields
from end_point.api.restplus import api
from end_point.api.api_get_nodes_graph_service import config


get_nodes_fields = api.model('GetNodes', {
    config.CYTOGRAPH:fields.Raw(required=True, description=config.CYTOGRAPH_DESC ),  
    config.COLOR_LIST:fields.List(fields.Raw(),required=True, description=config.COLOR_LIST_DESC),    
    "message": fields.String(required=True)
    })
