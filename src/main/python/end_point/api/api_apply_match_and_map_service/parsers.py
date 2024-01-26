from flask_restx import fields, reqparse
from end_point.api.restplus import api
from end_point.api.api_apply_match_and_map_service import config

app_match_maparg_json_model = api.model(
    "AppMMRequest",
    {
        config.APMM_TEXTAREA: fields.String(required=True, description=config.APMM_DESCRIPTION),
    },
)

app_match_mapparser = reqparse.RequestParser()
app_match_mapparser.add_argument(config.APMM_TEXTAREA, required=True, help=config.APMM_DESCRIPTION, type=str)