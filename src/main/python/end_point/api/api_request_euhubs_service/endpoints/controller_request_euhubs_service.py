
from flask_restx import Resource
from end_point.api.restplus import api
from end_point.api.api_request_euhubs_service.serializers import request_euhubs_fields
from end_point.business.controllers.controller_request_euhubs.tasks import controller_request_euhubs_task
from end_point.api.api_request_euhubs_service import config

ns = api.namespace(config.APP_URL, description=config.CONTROLLER_REQUEST_EUHUBS_DESCP)

@ns.route('')
class GetEuhubs(Resource):

    @ns.marshal_with(request_euhubs_fields)
    def post(self):
        """
        :GET request which returns the Title of consulted EuHubs4data datasets.
        """
        return controller_request_euhubs_task() 