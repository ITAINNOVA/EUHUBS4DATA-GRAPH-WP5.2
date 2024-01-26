
from end_point.logging_ita import application_logger
import end_point.config as config
from multiprocessing.pool import ThreadPool
from end_point.business.services.ckan_updater.ckan_importer import CkanImporter


class Mapper():
    """
    Class used for mapping tasks.
    It is used by the controllers
    """

    def __init__(self, matchandmap, wrapper):
        # Gathers useful classes
        self.matchandmap = matchandmap
        self.wrapper = wrapper
        self.already_done = False

    def install_ontologies(self):
        """
        Install the ontologies if they have not been installed already.
        """
        if not self.already_done:
            # Importing Ontologies
            application_logger.info('Importing Ontologies...')
            
            # Install the main ontology
            self.dcat_main_ontology = self.wrapper.downloader.install_one_ontology(
                config.DCAT_CORE_MAIN, config.DCAT_MAIN_ONTOLOGY, 
                config.IDS_CORE_FORMAT, config.IDS_CORE_FORMAT_LOW_CHARACTERS, 
                download_bool=False, dcat=True)
            
            # Set already_done flag to True
            self.already_done = True
        else:
            # Reset the graph using the writing graph
            self.dcat_main_ontology.reset_graph(
                self.wrapper.downloader.return_writing_graph())
        
        # Log the completion of importing ontologies
        application_logger.info('Ontologies have been imported')

    def aux_updating_index_function(self, uri_list_result):
        """
        Updates the search index with the new nodes saved on the database
        """
        application_logger.info('Updating index...')
        for dataset_uri in uri_list_result:
            application_logger.info(f"Dataset URI: {str(dataset_uri)}")
            try:
                self.wrapper.search_index.parse_dict_and_update_consulting(
                    self.wrapper.database_conector.request_all_node_information(dataset_uri))
            except Exception as e:
                application_logger.error(f"Exception caugth: {str(e)}")
                application_logger.error(e, exc_info=True)
        application_logger.info("Update done!")

    def map_metadata_base(self, metadata_list, class_query, property_query=config.NODE_PROPERTY_NAME):
        """
        Maps the metadata of the datasets provided in the parameter "metadata_list" to the local ontologies

        Args:
            metadata_list (list): List of datasets
            class_query (str): Class most likely to be mapped
            property_query (URIRef): _description_. Defaults to config.NODE_PROPERTY_NAME.

        Returns:
            list: List of nodes saved on database after mapping metadata
        """
        self.matchandmap.install_ontologies()
        ontology_access = self.matchandmap.main_ontology
        uri_list_result = self.map_metadata(metadata_list, class_query, ontology_access,
                                            property_query=config.NODE_PROPERTY_NAME)
        return uri_list_result

    def map_metadata_dcat(self, metadata_list, class_query):
        """
        Maps the metadata of the datasets provided in the parameter "metadata_list" to the DCAT vocabulary

        Args:
            metadata_list (list): List of datasets
            class_query (str): Class most likely to be mapped
            property_query (URIRef): _description_. Defaults to config.NODE_PROPERTY_NAME.

        Returns:
            list: List of nodes saved on database after mapping metadata
        """
        self.install_ontologies()
        ontology_access = self.dcat_main_ontology
        uri_list_result = self.map_metadata(metadata_list, class_query, ontology_access,
                                            property_query=config.NODE_PROPERTY_NAME)
        pool = ThreadPool(2)
        try:

            application_logger.info("Updating ElastiSearch file!")
            application_logger.info(uri_list_result)
            pool.apply_async(self.aux_updating_index_function,
                             args=(uri_list_result, ))
        except Exception as e:
            application_logger.error(
                f"Exception caugth while updating ElasticSearch: {str(e)}")
            application_logger.error(e, exc_info=True)
        try:
            ckan_importer = CkanImporter()
            application_logger.info("Importing to CKAN...!")
            pool.apply_async(ckan_importer.ckan_mapper,
                             args=(metadata_list, uri_list_result, ))

        except Exception as e:
            application_logger.error(
                f"Exception caugth while mapping properties: {str(e)}")
            application_logger.error(e, exc_info=True)
        pool.close()
        pool.join()
        return uri_list_result

    def map_metadata(self, metadata_list, class_query, ontology_access, property_query=config.NODE_PROPERTY_NAME):
        """
        Map metadata to a class in the ontology and return the resulting URI list.
        
        Args:
            metadata_list (list or object): List of metadata or a single metadata object.
            class_query (str): Class query to match metadata against.
            ontology_access (object): Object providing access to the ontology.
            property_query (str, optional): Property query to match metadata against. Defaults to config.NODE_PROPERTY_NAME.

        Returns:
            list: List of URIs resulting from the mapping.
        """
        uri_list_result = list()

        # Convert single metadata object to a list if needed
        if type(metadata_list) is not list:
            metadata_list = [metadata_list]

        # Perform the mapping if the metadata list is not empty
        if len(metadata_list) > 0:
            try:
                # Call the ontology access method to map metadata to class
                uri_list_result = ontology_access.mapping_metadata_to_class(
                    metadata_list, class_query, property_query=property_query,
                    matchandmap=self.matchandmap, search_index=self.wrapper.search_index)

                # Log successful mapping
                application_logger.info("All threads have finished their tasks!")
            except Exception as e:
                # Log any exception that occurred during mapping
                application_logger.error(f"Exception caught while mapping properties: {str(e)}")
                application_logger.error(e, exc_info=True)

        return uri_list_result
