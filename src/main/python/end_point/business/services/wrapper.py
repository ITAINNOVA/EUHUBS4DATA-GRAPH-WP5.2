
from rdflib import Graph
from end_point.business.services.search_services.search_index import SemanticSearchIndex
from end_point.business.services.search_services.database import DatabaseConnector
from end_point.business.services.ontology.complementary.data_extration_euhub import ExtrationData
from end_point.business.services.ontology.complementary.ontology_downloader import OntologyDownloader
import end_point.config as config
from end_point.business import utils
from end_point.logging_ita import application_logger
from end_point.config import db_cache


class Wrapper():
    """
    Class which main function is to gather other classes
    in other to emulate the singleton pattern and being
    able to used them in any part of the program.
    Gathers utilities
    """

    def __init__(self):
        self.database_conector = DatabaseConnector()
        self.extrator = ExtrationData(config.JOYCE_URL)
        self.search_index = SemanticSearchIndex()
        writing_graph = Graph()
        self.downloader = OntologyDownloader(writing_graph, self.database_conector)

    def map_to_cytospace(self, json_neo4j_content, size_score=10):
        """ Function which maps the content in Neo4j Json format to
        Cytoscape json format

        Args:
            json_neo4j_content (dictionarty):Neo4j json format database content
            size_score (int, optional): _description_. Defaults to 1.

        Returns:
            dictionary : Cytoscape json format
        """
        elements = {}
        node_label = None
        list_labels_added = list()
        try:
            original_json = json_neo4j_content.get("results")
            if original_json:
                original_json = original_json[0]
                original_json = original_json.get("data")
                if original_json:
                    node_elements = []
                    node_edges = []
                    for graph in original_json:
                        graph = graph.get("graph")
                        nodes = graph.get("nodes")
                        relationships = graph.get("relationships")
                        if nodes:
                            for node in nodes:
                                node_id = node.get('id')
                                if node.get('labels'):
                                    labels = node.get('labels')
                                    if type(labels) is list and len(labels) > 0:
                                        if len(labels) > 1:
                                            node_label = labels[1]
                                        else:
                                            node_label = labels[0]
                                    else:
                                        node_label = labels
                                    if node_label:
                                        node_label = utils.delete_ontology_preffix(
                                            node_label)
                                node_title = None
                                if node.get('properties'):
                                    node_properties = node.get('properties')

                                    for key, value in node_properties.items():
                                        if ("title" in key) or ("name" in key):
                                            if type(value) is list:
                                                node_title = value[0]
                                            else:
                                                node_title = value
                                    if node_properties and node_label:
                                        node_properties['Class'] = node_label

                                colorid = config.db_cache.get_color_class(
                                    node_label)
                                if not colorid:
                                    colorid = utils.get_random_colour()
                                    config.db_cache.add_class_color(
                                        colorid, node_label)
                                if not (node_label in list_labels_added):
                                    db_cache.add_temp_class_color({
                                        'color': colorid,
                                        'classe': node_label
                                    })
                                    list_labels_added.append(node_label)
                                if not node_title:
                                    node_title = node_label
                                node_elements.append({
                                    'data': {
                                        'id': node_id, 'label': f"{str(node_title)}", 'colorid': colorid,
                                        'attributes': utils.create_html_from_json(node_properties),
                                        'size_node': 10 * size_score
                                    }
                                })
                        else:
                            application_logger.error(
                                f"Exception caught mapping Neo4j graph format to CytoScape format, NO NODES")
                        for relation in relationships:

                            node_edges.append({
                                'data':  {'id': str(relation.get('id')), 'source': str(relation.get('startNode')), 'target': str(relation.get('endNode')), 'label': utils.delete_ontology_preffix(str(relation.get('type')))}
                            })
                    elements['nodes'] = node_elements
                    elements['edges'] = node_edges
                else:
                    application_logger.error(
                        f"Exception caught mapping Neo4j graph format to CytoScape format, NO DATA")
            else:
                application_logger.error(
                    f"Exception caught mapping Neo4j graph format to CytoScape format, NO Results")

        except Exception as e:
            application_logger.error(e, exc_info=True)
            application_logger.error(
                f"Exception caught mapping Neo4j graph format to CytoScape format: {str(e)}")

        return elements


wrapper = Wrapper()
