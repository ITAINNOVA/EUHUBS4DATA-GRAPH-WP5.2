
from flask_restx import Resource
from end_point.api.restplus import api
from end_point import config as settings
from end_point.api.api_get_rdf_file_ontology_service import config

ns = api.namespace('get_ontology', description=config.GETONTOLOGY_DESC)
from end_point.business.controllers.controller_get_rdf.tasks import  controller_get_rdf

@ns.route('')
class GetRDFOntologyFile(Resource):

    def get(self):
        """
        GET request retrieves the updated ontology.
        """
        return controller_get_rdf(settings.EXTENDED_ONTOLOGY)
