from flask_restx import fields
from end_point.api.restplus import api
from end_point.api.api_apply_match_and_map_service import config

app_match_mapfields = api.model('AppMM', {
    config.APMM_URI_LIST: fields.List(fields.String(), required=True, description=config.APMM_URI_LIST_DESP),    
    config.MESSAGE: fields.String(required=True)
    })
