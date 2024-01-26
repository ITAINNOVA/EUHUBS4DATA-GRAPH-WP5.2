
from flask_restx import Resource
from end_point.api.restplus import api
from end_point.api.api_get_rdf_file_service import config
from end_point.business.controllers.controller_get_rdf.tasks import  controller_get_rdf

ns = api.namespace('get-rdf', description=config.RDF_FILE_DESC)

@ns.route('/<string:rdf_filename>')
class GetRDFFilename(Resource):
    def get(self, rdf_filename):
        """
        This :GET request retrieves the asked RDF file
        """
        return controller_get_rdf(rdf_filename)