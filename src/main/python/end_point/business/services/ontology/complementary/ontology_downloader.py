
import wget
import pandas as pd
import os
from end_point.business import utils
from end_point.business.services.ontology.complementary.ontology_access import OntologyAccess
from end_point.business.services.ontology.complementary.subontology.dcat_ontology_access import DACTAccess
import end_point.config as config
from end_point.logging_ita import application_logger
import subprocess
from rdflib import Graph


class OntologyDownloader:
    """
    Class used with the purpose of download ontologies from file 'list_ontology.csv'
    so as to create a dictionary with contains theses ontologies loaded as RDFlib
    graph
    """

    def __init__(self, writing_graph, database_conector):
        self.writing_graph = writing_graph
        self.base_resource_path = os.path.join(
            os.path.dirname(config.APP_RESOURCES), 'ontology/')
        self.config_file = self.base_resource_path + 'list_ontology.csv'
        self.database_conector = database_conector
        self.dict_ontologies = dict()

    def check_class_belong_ontology(self, uri_class, ontology_uri):
        """ Confirms if the uri provided belongs to the ontology uri

        Args:
            uri_class ([str]): String, Uri of a class
            ontology_access ([str]): String, Uri of an ontology
        Example:
            uri_class = "https://w3id.org/idsa/core/DataResource"
            ontology_access = "https://w3id.org/idsa/core/"
            In this case it will return True

        Returns:
            [bool]: In case the class belongs to the ontology it will return True
        """
        not_download_needed = False
        if ontology_uri.ONTOLOGY_URI in uri_class:
            not_download_needed = True

        return not_download_needed

    def return_writing_graph(self):
        """
        Returns the writing graph.

        Returns:
            writing_graph: The writing graph.
        """
        return self.writing_graph

    def restart_graph_ontologies(self):
        # Create a new Graph object to replace the existing writing_graph
        self.writing_graph = Graph()

        # Iterate through the dictionary of ontologies
        for key, ontology in self.dict_ontologies.items():
            # Reset the graph of each ontology, passing in the new writing_graph
            ontology.reset_graph(self.writing_graph)

    def install_ontologies(self):
        """ Install all the available ontologies in the file "list_ontology.csv"

        Returns:
            [list(OntologyAccess)]: List composed by OntologyAcess classes, these
            classes represent the ontologies installed on the database
        """
        dict_ontologies = dict()
        df = pd.read_csv(self.config_file)
        application_logger.info(f'Creating file for NER predictions...')
        dict_ontology_uris = dict()
        for index, row in df.iterrows():
            # URI of the ontology
            uri_url = row['uri_onto']
            # Download URL
            download_url = row['download_url']
            # Format of the file to be imported in the database
            format_file = row['format_file']
            # Format of the file to loaded in the graph
            format_parse = row['format_parse']

            ner_prediction = row['ner_prediction']

            application_logger.info(
                f'{str(uri_url)} - {str(format_file)} - {str(format_parse)}')

            if not dict_ontology_uris.get(uri_url):
                application_logger.info(
                    f'Creating new Access Ontology... -> {str(ner_prediction)} -> {str(uri_url)}')

                if "http" in download_url:
                    new_ontology = self.install_one_ontology(
                        uri_url, download_url, format_file, format_parse, download_bool=True, import_ontology=False)
                else:
                    new_ontology = self.install_one_ontology(
                        uri_url, download_url, format_file, format_parse, download_bool=False, import_ontology=False)

            else:
                application_logger.info(f'Access already created...')
                new_ontology = dict_ontology_uris.get(uri_url)

            # If the ontology is installed
            if new_ontology:
                dict_ontologies[ner_prediction] = new_ontology
                dict_ontology_uris[uri_url] = new_ontology
            else:
                application_logger.warning("It could not load the ontology!")
        application_logger.info(f'All ontologies have been imported')
        if dict_ontologies:
            self.dict_ontologies = dict_ontologies
        return dict_ontologies

    def install_one_ontology(self, uri_url, download_url, format_file, parse_format, download_bool, import_ontology=True, dcat=False):
        """ Install one ontology, this includes importing the ontology on the database
            and loading it on a RDFlib graph.

        Args:
            uri_url ([str]): Uri of the ontology
            parse_format ([str]): Format of the file to loaded in the graph
            download_url ([str]): URL to download the ontology file
            format_file ([str]): Format of the file to be imported in the database

        Returns:
            [OntologyAccess]: Class used to access to the ontology
        """
        new_ontology = None
        filename = None
        try:
            if download_bool:
                filename, rootname = utils.build_filename(
                    "ontology", self.base_resource_path)
                application_logger.info("Downloading...")
                response = wget.download(download_url, filename)

                application_logger.info("Creating access...")

                if dcat:
                    application_logger.warning("DCAT ONTOLOGY")
                    new_ontology = DACTAccess(uri_url, filename, self.database_conector,
                                              parse_format, self.writing_graph)
                else:
                    new_ontology = OntologyAccess(
                        uri_url, filename, self.database_conector, parse_format, self.writing_graph)
                if import_ontology:
                    application_logger.info("Importing file...")
                    self.database_conector.remote_import_file(
                        download_url, format_file)
                try:
                    os.remove(filename)
                except Exception as e:
                    application_logger.error(
                        f' It was no possible to remove the file: {str(e)}')
                    application_logger.error(e, exc_info=True)
            else:
                filename = config.APP_ONTOLOGY + download_url
                p = subprocess.call(['chmod', '0777', filename])

                application_logger.info(f"{filename} file detected")

                path_file = f"http://{config.HOST_NAME}:{str(os.environ.get('FLASK_APP_PORT'))}/api/get-rdf/" + download_url
                application_logger.info("Creating access...")

                if dcat:
                    application_logger.info("DCAT ONTOLOGY")
                    new_ontology = DACTAccess(uri_url, filename, self.database_conector,
                                              parse_format, self.writing_graph)
                else:
                    new_ontology = OntologyAccess(
                        uri_url, filename, self.database_conector, parse_format, self.writing_graph)
                if import_ontology:
                    application_logger.info("Importing file...")
                    self.database_conector.remote_import_file(
                        path_file, format_file)

        except Exception as e:
            application_logger.error(
                f'Error importing file: {str(e)} , file URL: {download_url}')
            application_logger.error(e, exc_info=True)
            if download_bool:
                try:
                    if filename:
                        os.remove(filename)
                except Exception as e:
                    application_logger.error(
                        f' It was no possible to remove the file: {str(e)}')
                    application_logger.error(e, exc_info=True)

        return new_ontology
