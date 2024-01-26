from flask_restx import fields

from end_point.api.restplus import api
from end_point.api.api_evaluate_ontology_array_service import config

ontology_metrics_array_fields = api.model('MetricsArray', {
    config.METRICS: fields.Raw(required=True, description='The task details'),    
    "message": fields.String(required=True)
    })

