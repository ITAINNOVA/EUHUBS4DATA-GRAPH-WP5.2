
from flask_restx import Resource
from end_point.api.restplus import api
from end_point.api.api_apply_match_and_map_service.serializers import app_match_mapfields
from end_point.api.api_apply_match_and_map_service.parsers import app_match_maparg_json_model,app_match_mapparser
from end_point.api.api_apply_match_and_map_service import config as settings

ns = api.namespace(settings.APP_URL, description=settings.APMM_DESCRIPTION)
from end_point.business.controllers.controller_match_and_map.tasks import controller_match_and_map_task


@ns.route('')
class GetAppMM(Resource):

    @ns.marshal_with(app_match_mapfields)
    @ns.expect(app_match_maparg_json_model)
    def post(self):
        """
        Given a plain text through the requests object
        applies the algorithm Match&Map to this plain text,
        mapping the result triplets in the database.
        It returns the url to download a turtle format file with the rdf
        triplets which have been created and it also returns a json file which contains the structure of the new graph created on Neo4j.
        'uri_list': List with the uris of the created nodes.
             
        """
        request_args = app_match_mapparser.parse_args()
        return controller_match_and_map_task(request_args['textarea'])