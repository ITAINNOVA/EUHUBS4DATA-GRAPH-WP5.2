
import os
import json
import end_point.config as config
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Response, send_from_directory
from end_point.business.services.evaluation.oquare_service import OQuareMetrics
from end_point.business.services.knowledge_graph.matchandmap import MatchAndMap
from end_point.business.services.ontology.mapper import Mapper
from end_point.business.services.wrapper import wrapper
from end_point.logging_ita import application_logger
from end_point.config import db_cache, ids_db_cache, base_ids_db_cache

# Change the format of the CYPHER
# MATCH (n) WHERE datetime(head(n.`https://w3id.org/idsa/core/node_created`)) > datetime('2015-06-24T12:50:35.556+0100') return n
# https://stackoverflow.com/questions/69898673/docker-compose-persistent-volume-issue-with-elasticsearch
# https://stackoverflow.com/questions/21214270/how-to-schedule-a-function-to-run-every-hour-on-flask
# APScheduler Doc: https://apscheduler.readthedocs.io/en/latest/
# daemon=True: https://docs.python.org/3.4/library/threading.html#thread-objects
matchAndmap = MatchAndMap(wrapper)
mapper = Mapper(matchAndmap, wrapper)

def job_function():
    """
    This function calculates the metrics using OQuareMetrics.
    It requests the metrics cache for the extended and base IDs ontologies.
    # os.system(f'java -jar src/main/java/oquare-versions.jar --ontology {str(config.EXTENDED_IDS_ONTOLOGY_PATH)}  --outputFile {str(config.OQUARE_IDS_XML)} --reasoner ELK')
    # os.system(f'java -jar src/main/java/oquare-versions.jar --ontology {str(config.BASE_IDS_ONTOLOGY_PATH)}  --outputFile {str(config.OQUARE_BASE_XML)} --reasoner ELK')
    # os.system(f'java -jar src/main/java/oquare-versions.jar --ontology {str(config.EXTENDED_IDS_ONTOLOGY_PATH)}  --outputFile {str(config.OQUARE_IDS_XML)} --reasoner ELK') 
    
    """
    # Log the start of the calculation
    application_logger.info("Let's calculate the metrics...")

    # Calculate the metrics for the extended IDs ontology
    oquare_metrics = OQuareMetrics()
    try:
        oquare_metrics.request_metrics_cache(
            ids_db_cache, config.EXTENDED_IDS_ONTOLOGY_PATH, config.OQUARE_IDS_XML, config.JAVA_PATH_JAR)
    except Exception as e:
        # Log any exceptions that occur during the calculation
        application_logger.error(f"Exception caught while processing metrics: {str(e)}")
        application_logger.error(e, exc_info=True)

    # Calculate the metrics for the base IDs ontology
    try:
        oquare_metrics.request_metrics_cache(
            base_ids_db_cache, config.BASE_IDS_ONTOLOGY_PATH, config.OQUARE_BASE_XML, config.JAVA_PATH_JAR)
    except Exception as e:
        # Log any exceptions that occur during the calculation
        application_logger.error(f"Exception caught while processing metrics: {str(e)}")
        application_logger.error(e, exc_info=True)

    # Log the completion of the job
    application_logger.info("Job done!")

# Do your work here
job_function()
# Shutdown your cron thread if the web process is stopped
sched = BackgroundScheduler(daemon=True)
sched.add_job(job_function, 'interval', days=7)
sched.start()


def request_metadata_euhubs(name=None, is_repo=None, description=None, domains=None, location=None,license=None, formats=None, privacy=None, publisher=None, language=None, issued=None, creator=None, from_augmented_time=None, from_upload_time=None, url=None, rdf_url=None, landing_page=None, spatial=None, similarity=None, source=None, team=None, is_author=None, modified=None):
    """
    Request metadata from EUHubs.
    Args:
        name (str): The name of the dataset.
        is_repo (bool): Whether the dataset is a repository.
        description (str): The description of the dataset.
        domains (list[str]): The domains of the dataset.
        location (str): The location of the dataset.
        license (str): The license of the dataset.
        formats (list[str]): The formats of the dataset.
        privacy (str): The privacy level of the dataset.
        publisher (str): The publisher of the dataset.
        language (str): The language of the dataset.
        issued (str): The issued date of the dataset.
        creator (str): The creator of the dataset.
        from_augmented_time (str): The starting augmented time of the dataset.
        from_upload_time (str): The starting upload time of the dataset.
        url (str): The URL of the dataset.
        rdf_url (str): The RDF URL of the dataset.
        landing_page (str): The landing page of the dataset.
        spatial (str): The spatial coverage of the dataset.
        similarity (str): The similarity of the dataset.
        source (str): The source of the dataset.
        team (str): The team of the dataset.
        is_author (bool): Whether the user is the author of the dataset.
        modified (str): The modified date of the dataset.
    Returns:
        list: The list of metadata.
    """
    # Open this select menu
    if domains:
        if "Open this select menu" in domains:
            domains = None

    if location:
        if "Open this select menu" in location:
            location = None
    metadata_list = wrapper.extrator.search_default_datasets(name, is_repo, description, domains, location,license, formats, privacy, publisher, language, issued, creator, from_augmented_time, from_upload_time, url, rdf_url, landing_page, spatial, similarity, source, team, is_author, modified) 
    return metadata_list


def controller_find_ontologies():
    """
    Returns a list with the uri of all ontologies availables in the file list_ontology.csv
    """
    response_content = []
    try:
        list_ontologies = list()
        df = pd.read_csv(config.APP_RESOURCES +
                         str('ontology/list_ontology.csv'))
        for index, row in df.iterrows():
            uri_url = {'key': row.get('uri_onto'), 'name': row.get('uri_onto')}
            if uri_url not in list_ontologies:
                list_ontologies.append(uri_url)
        list_ontologies.append(
            {'key': config.IDS_CORE_MAIN_ONTOLOGY, 'name': config.IDS_CORE_MAIN_ONTOLOGY})
        response_content = list_ontologies
    except Exception as e:
        application_logger.error(f"Exception caugth: {str(e)}")
    return Response(json.dumps(response_content), mimetype='application/json')


def controller_find_locations():
    """
    Returns the available countries  on https://euhubs4data.eu/datasets/
    """
    return Response(json.dumps(config.COUNTRIES_KEY_NAME), mimetype='application/json')


def controller_find_domains():
    """
    Returns the domains for datasets on https://euhubs4data.eu/datasets/
    """
    return Response(json.dumps(config.FIELDS_KEY_NAME), mimetype='application/json')


def controller_favicon():
    """
    Responses with the icon of the application
    Flask official tutorial:
        https://flask.palletsprojects.com/en/2.0.x/patterns/favicon/
    """
    return send_from_directory(os.path.join(config.STATICS_PATH, 'icon'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def aux_graph_visualize(list_uri, list_graph_result):
    """
    Visualize the graph data for a list of URIs.

    Args:
        list_uri (list): List of URIs.
        list_graph_result (list): List to store the graph results.

    Returns:
        tuple: A tuple containing the list of nodes, list of edges, and updated list of graph results.
    """
    list_nodes = []
    list_edges = []
    i = 0
    db_cache.new_tmp_class_color()
    try:
        while i < len(list_uri):
            uri = list_uri[i].get('uri')
            json_graph = wrapper.database_conector.request_all_node_information(uri)
            list_graph_result.append(json_graph)
            graph_result = wrapper.map_to_cytospace(json_graph, list_uri[i].get('score'))
            if graph_result.get('nodes'):
                list_nodes += graph_result.get('nodes')
            if graph_result.get('edges'):
                list_edges += graph_result.get('edges')

            i += 1
    except Exception as e:
        application_logger.error(f"Exception caught while appending content: {str(e)}")
    return list_nodes, list_edges, list_graph_result
