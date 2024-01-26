
import logging
from flask_restx import Resource
from end_point.api.restplus import api
from end_point.api.api_request_title_euhubs_service.serializers import request_euhubs_fields
from end_point.business.controllers.controller_request_title_euhubs.tasks import controller_request_title_task
from end_point.api.api_request_title_euhubs_service import config

log = logging.getLogger(__name__)
ns = api.namespace(config.APP_URL, description=config.REQUEST_TITLE_EUHUBS)

@ns.route('')
class PostTitleEUHUBS(Resource):

    @ns.marshal_with(request_euhubs_fields)
    def post(self):
        """
        :POST requests which returns the title of the available datasets.
        """  
        return controller_request_title_task()

    @ns.marshal_with(request_euhubs_fields)
    def get(self):
        """
        :GET requests which returns the title of the available datasets.
        """  
        return controller_request_title_task()      