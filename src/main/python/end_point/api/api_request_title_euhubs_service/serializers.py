from flask_restx import fields

from end_point.api.restplus import api
from end_point.api.api_request_title_euhubs_service import config

#{"dataset_name": value}
request_dataset = api.model('dataset_name_objet',{
    "dataset_name":fields.String(required=True)
})
request_euhubs_fields = api.model('EuhubsTitle', {
    "dataset_list": fields.List(fields.Raw, required=False, description=config.TITLE_LIST_DESCP),      
    "message": fields.String(required=False)
})

