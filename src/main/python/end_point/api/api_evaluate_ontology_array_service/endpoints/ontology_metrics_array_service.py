
from flask_restx import Resource
from end_point.api.restplus import api
from end_point.api.api_evaluate_ontology_array_service.serializers import ontology_metrics_array_fields
from end_point.api.api_evaluate_ontology_array_service import config as settings
from end_point.logging_ita import application_logger
from end_point.config import ids_db_cache
from end_point.config import base_ids_db_cache
from end_point.api.api_evaluate_ontology_array_service import config
from end_point.business.services.evaluation.oquare_service import OQuareMetrics


def controller_evaluate_ontology_array():
    """
    Evaluates the ontology array and returns the metrics in JSON format.

    Returns:
        json_metrics (dict): The ontology metrics in JSON format.
        message (str): A message indicating the status of the evaluation.
    """
    json_metrics = dict()
    message = None
    oquare_metrics = OQuareMetrics()
    try:
        # Get the saved data
        application_logger.info("Let's get the saved data")

        ontology_json_metrics = dict()

        # Build JSON from cache for ids_db_cache
        json_core = oquare_metrics.build_json_from_cache(ids_db_cache)
        ontology_json_metrics['ids'] = json_core

        application_logger.info("IDS ontology metrics")

        # Build JSON from cache for base_ids_db_cache
        json_core = oquare_metrics.build_json_from_cache(base_ids_db_cache)
        ontology_json_metrics['base'] = json_core

        # Job done!
        application_logger.info("Job done!")

        json_metrics = ontology_json_metrics
        message = "Job done!"
    except Exception as e:
        message = f"Server error, it has crashed Exception caught: {str(e)}"
        application_logger.error(message)
        application_logger.error(e, exc_info=True)
        
    return json_metrics, message

ns = api.namespace(settings.APP_URL, description=settings.EVALUATEONTOLGY_DESCP)

@ns.route('')
class GetMetricsArray(Resource):

    @ns.marshal_with(ontology_metrics_array_fields)
    def get(self):
        """
        :GET request which returns the evaluation metrics of an ontology
        """      
        json_metrics, message = controller_evaluate_ontology_array()
        return {config.METRICS: json_metrics, 'message': message}

