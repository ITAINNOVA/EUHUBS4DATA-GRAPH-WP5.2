
from flask_restx import Resource
from end_point.api.restplus import api
from end_point.business.controllers.controller_get_rdf.tasks import controller_get_rdf
from end_point import config as settings
from end_point.api.api_get_base_rdf_file_ontology_service import config

ns = api.namespace('get_base_ontology', description=config.RETURN_BASE_ONTOLGY_DESC)


@ns.route('')
class GetBaseOntology(Resource):

    def get(self):
        """
        This :GET request retrieves the base ontology.
        """
        return controller_get_rdf(settings.MAIN_ONTOLOGY_FILE)