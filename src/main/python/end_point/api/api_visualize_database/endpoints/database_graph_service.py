
from flask_restx import Resource
from end_point.api.restplus import api
from end_point.business.controllers.controller_visualize_database.tasks import controller_visualize_database
from end_point.api.api_visualize_database import config
ns = api.namespace('database_graph', description=config.DATABASE_GRAPH_SERVICE_DESC_JOB)

@ns.route('')
class GetDatabaseGraph(Resource):

    def get(self):
        """
        :GET request return the graph result as cytospace graph format
        """
        return controller_visualize_database()