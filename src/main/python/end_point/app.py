# Run a test server.
# Import flask and template operators
import os
from flask import Flask, Blueprint
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import render_template
# https://flask.palletsprojects.com/en/1.1.x/config/

from end_point import config as settings
from end_point.business.controllers.controllers import controller_find_domains, controller_find_ontologies, controller_favicon,controller_find_locations 
# Define the WSGI application object
application = Flask(__name__,template_folder=settings.TEMPLATE_PATH,static_folder=settings.STATICS_PATH)

application.wsgi_app = ProxyFix(application.wsgi_app)

@application.route('/view_database_graph', methods=['GET'])
def view_database_graph():
    return render_template("view_graph.html")

@application.route('/view_nodes', methods=['GET'])
def view_nodes_ontology():
    return render_template("view_node.html")


@application.route('/view_charts', methods=['GET'])
def view_charts_ontology():
    return render_template("view_chart.html")

@application.route('/dataset/<uri_node>', methods=['POST', 'GET'])
def show_nodes(uri_node):
    return render_template("view_node.html")

# Main page
@application.route('/', methods=['GET'])
def main_menu():
    return render_template("home.html")

@application.route('/_find_ontologies', methods=['GET'])
def route_find_ontologies():
    return controller_find_ontologies()

@application.route('/favicon.ico')
def favicon():
    return controller_favicon()


@application.route('/_find_locations', methods=['POST', 'GET'])
def get_find_locations():
    return controller_find_locations()


@application.route('/_find_domains', methods=['POST', 'GET'])
def get_find_domains():
    return controller_find_domains()


from end_point.api.restplus import api

from end_point.api.api_apply_match_and_map_service.endpoints.apply_match_and_map_service import ns as wo_match_and_map_namespace
from end_point.api.api_evaluate_ontology_array_service.endpoints.ontology_metrics_array_service import ns as wo_ontology_metrics_array_namespace
from end_point.api.api_get_nodes_service.endpoints.get_node_service import ns as wo_get_nodes_namespace

from end_point.api.api_request_euhubs_service.endpoints.controller_request_euhubs_service import ns as wo_request_euhubs_namespace
from end_point.api.api_request_title_euhubs_service.endpoints.controller_request_euhubs_service import ns as wo_request_title_euhubs_namespace
from end_point.api.api_visualize_database.endpoints.database_graph_service import ns as wo_visualize_database_namespace

from end_point.api.api_get_base_rdf_file_ontology_service.endpoints.get_base_ontology_service import ns as base_rdf_file_ontology_namespace
from end_point.api.api_get_nodes_graph_service.endpoints.get_nodes_graph_service import ns as wo_nodes_graph_namespace
from end_point.api.api_get_rdf_file_ontology_service.endpoints.get_rdf_file_ontology_service import ns as wo_rdf_file_ontology_namespace
from end_point.api.api_get_rdf_file_service.endpoints.get_rdf_file_service import ns as wo_rdf_file_namespace
from end_point.api.api_semantic_search_nodes_service.endpoints.semantic_search_node_service import ns as wo_semantic_search_node_namespace

os.environ["TOKENIZERS_PARALLELISM"] = "false"
application.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTX_SWAGGER_UI_DOC_EXPANSION
application.config['RESTX_VALIDATE'] = settings.RESTX_VALIDATE
application.config['RESTX_MASK_SWAGGER'] = settings.RESTX_MASK_SWAGGER
application.config['ERROR_404_HELP'] = settings.RESTX_ERROR_404_HELP

blueprint_api = Blueprint('api', __name__, url_prefix='/api')
api.init_app(blueprint_api)
   
api.add_namespace(wo_match_and_map_namespace)
api.add_namespace(wo_ontology_metrics_array_namespace)
api.add_namespace(wo_get_nodes_namespace)
api.add_namespace(wo_request_euhubs_namespace)
api.add_namespace(wo_request_title_euhubs_namespace)
api.add_namespace(wo_visualize_database_namespace)
api.add_namespace(base_rdf_file_ontology_namespace)
api.add_namespace(wo_nodes_graph_namespace)
api.add_namespace(wo_rdf_file_ontology_namespace)
api.add_namespace(wo_rdf_file_namespace)
api.add_namespace(wo_semantic_search_node_namespace)
   
application.register_blueprint(blueprint_api)

application.debug = settings.FLASK_DEBUG