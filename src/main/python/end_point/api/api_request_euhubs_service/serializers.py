from flask_restx import fields

from end_point.api.restplus import api
from end_point.api.api_request_euhubs_service import config

request_euhubs_fields = api.model('Euhubs', {
    "uri_list": fields.List(fields.String, required=True, description=config.URI_LIST_DESCP),      
    "message": fields.String(required=True)
    })


