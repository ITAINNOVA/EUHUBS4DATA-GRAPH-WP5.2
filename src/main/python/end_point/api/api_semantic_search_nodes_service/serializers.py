from flask_restx import fields
from end_point.api.restplus import api
from end_point.api.api_semantic_search_nodes_service import config


semantic_search_fields = api.model('SemanticSearch', {
    config.COLOR_CLASS: fields.List(fields.Raw(),required=True, description=config.COLOR_CLASS_DESC),    
    config.JSON_CONTENT : fields.Raw(required=True, description=config.JSON_CONTENT_DESC),    
    config.GRAPH_CONTENT: fields.Raw(required=True, description=config.GRAPH_CONTENT_DESC),      
    "message": fields.String(required=True)
    })
