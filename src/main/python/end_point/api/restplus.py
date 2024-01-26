
import logging
import os
from flask_restx import Api
from end_point import config as settings

log = logging.getLogger(__name__)

api = Api(version='1.0', title=os.environ.get('HOST_NAME') + ' API', description='')

@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500
