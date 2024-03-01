
from multiprocessing.pool import ThreadPool
from end_point.business.services.ontology.complementary.ontology_access import *
from rdflib import URIRef, Literal
from rdflib.namespace import DCTERMS


class DACTAccess(OntologyAccess):
    """
    This class maps json dictionaries from https://euhubs4data.eu/datasets/ to DCAT vocabulary
    Object that extracts schema definitions from an rdf graph (or ontology).

    This class was implemented by using the source code available in:
        http://www.michelepasin.org/blog/2011/07/18/inspecting-an-ontology-with-rdflib
        https://github.com/lambdamusic/ontosPy

    Extracts data from International Data Spaces (IDS) Information Model.
    URL: https://international-data-spaces-association.github.io/InformationModel/docs/index.html

    GIT: https://github.com/RDFLib/rdflib

    Documentation:
    https://rdflib.readthedocs.io/en/stable/gettingstarted.html
    https://rdflib.readthedocs.io/en/stable/intro_to_creating_rdf.html

    https://wiki.uib.no/info216/index.php/Python_Examples

    https://buildmedia.readthedocs.org/media/pdf/rdflib/latest/rdflib.pdf

    """
    object_dcat_list = [
        URIRef("http://purl.org/dc/terms/issued"),
        URIRef("http://purl.org/dc/terms/Period"),
        URIRef("http://purl.org/dc/terms/Point"),
        URIRef("http://purl.org/dc/terms/abstract"),
        URIRef("http://purl.org/dc/terms/accessRights"),
        URIRef("http://purl.org/dc/terms/accrualMethod"),
        URIRef("http://purl.org/dc/terms/accrualPeriodicity"),
        URIRef("http://purl.org/dc/terms/accrualPolicy"),
        URIRef("http://purl.org/dc/terms/alternative"),
        URIRef("http://purl.org/dc/terms/audience"),
        URIRef("http://purl.org/dc/terms/available"),
        URIRef("http://purl.org/dc/terms/bibliographicCitation"),
        URIRef("http://purl.org/dc/terms/conformsTo"),
        URIRef("http://purl.org/dc/terms/contributor"),
        URIRef("http://purl.org/dc/terms/coverage"),
        URIRef("http://purl.org/dc/terms/created"),
        URIRef("http://purl.org/dc/terms/creator"),
        URIRef("http://purl.org/dc/terms/date"),
        URIRef("http://purl.org/dc/terms/dateAccepted"),
        URIRef("http://purl.org/dc/terms/dateCopyrighted"),
        URIRef("http://purl.org/dc/terms/dateSubmitted"),
        URIRef("http://purl.org/dc/terms/description"),
        URIRef("http://purl.org/dc/terms/educationLevel"),
        URIRef("http://purl.org/dc/terms/extent"),
        URIRef("http://purl.org/dc/terms/format"),
        URIRef("http://purl.org/dc/terms/hasFormat"),
        URIRef("http://purl.org/dc/terms/hasPart"),
        URIRef("http://purl.org/dc/terms/hasVersion"),
        URIRef("http://purl.org/dc/terms/identifier"),
        URIRef("http://purl.org/dc/terms/id"),
        URIRef("http://purl.org/dc/terms/instructionalMethod"),
        URIRef("http://purl.org/dc/terms/isFormatOf"),
        URIRef("http://purl.org/dc/terms/isPartOf"),
        URIRef("http://purl.org/dc/terms/isReferencedBy"),
        URIRef("http://purl.org/dc/terms/isReplacedBy"),
        URIRef("http://purl.org/dc/terms/isRequiredBy"),
        URIRef("http://purl.org/dc/terms/isVersionOf"),
        URIRef("http://purl.org/dc/terms/issued"),
        URIRef("http://purl.org/dc/terms/language"),
        URIRef("http://purl.org/dc/terms/license"),
        URIRef("http://purl.org/dc/terms/mediator"),
        URIRef("http://purl.org/dc/terms/medium"),
        URIRef("http://purl.org/dc/terms/modified"),
        URIRef("http://purl.org/dc/terms/provenance"),
        URIRef("http://purl.org/dc/terms/publisher"),
        URIRef("http://purl.org/dc/terms/references"),
        URIRef("http://purl.org/dc/terms/relation"),
        URIRef("http://purl.org/dc/terms/replaces"),
        URIRef("http://purl.org/dc/terms/requires"),
        URIRef("http://purl.org/dc/terms/rights"),
        URIRef("http://purl.org/dc/terms/rightsHolder"),
        URIRef("http://purl.org/dc/terms/source"),
        URIRef("http://purl.org/dc/terms/spatial"),
        URIRef("http://purl.org/dc/terms/subject"),
        URIRef("http://purl.org/dc/terms/tableOfContents"),
        URIRef("http://purl.org/dc/terms/title"),
        URIRef("http://purl.org/dc/terms/temporal"),
        URIRef("http://purl.org/dc/terms/type"),
        URIRef("http://purl.org/dc/terms/valid"),
        URIRef("http://www.w3.org/ns/dcat#Distribution"),
        URIRef("http://www.w3.org/ns/dcat#Relationship"),
        URIRef("http://www.w3.org/ns/dcat#Resource"),
        URIRef("http://www.w3.org/ns/dcat#Role"),
        URIRef("http://www.w3.org/ns/dcat#accessService"),
        URIRef("http://www.w3.org/ns/dcat#accessURL"),
        URIRef("http://www.w3.org/ns/dcat#byteSize"),
        URIRef("http://www.w3.org/ns/dcat#catalog"),
        URIRef("http://www.w3.org/ns/dcat#centroid"),
        URIRef("http://www.w3.org/ns/dcat#compressFormat"),
        URIRef("http://www.w3.org/ns/dcat#contactPoint"),
        URIRef("http://www.w3.org/ns/dcat#dataset"),
        URIRef("http://www.w3.org/ns/dcat#distribution"),
        URIRef("http://www.w3.org/ns/dcat#downloadURL"),
        URIRef("http://www.w3.org/ns/dcat#endDate"),
        URIRef("http://www.w3.org/ns/dcat#endpointDescription"),
        URIRef("http://www.w3.org/ns/dcat#endpointURL"),
        URIRef("http://www.w3.org/ns/dcat#hadRole"),
        URIRef("http://www.w3.org/ns/dcat#keyword"),
        URIRef("http://www.w3.org/ns/dcat#landingPage"),
        URIRef("http://www.w3.org/ns/dcat#mediaType"),
        URIRef("http://www.w3.org/ns/dcat#packageFormat"),
        URIRef("http://www.w3.org/ns/dcat#qualifiedRelation"),
        URIRef("http://www.w3.org/ns/dcat#record"),
        URIRef("http://www.w3.org/ns/dcat#servesDataset"),
        URIRef("http://www.w3.org/ns/dcat#service"),
        URIRef("http://www.w3.org/ns/dcat#spatialResolutionInMeters"),
        URIRef("http://www.w3.org/ns/dcat#startDate"),
        URIRef("http://www.w3.org/ns/dcat#temporalResolution"),
        URIRef("http://www.w3.org/ns/dcat#theme"),
        URIRef("http://www.w3.org/ns/dcat#themeTaxonomy")
    ]
    # Class                                     # Relationship
    dict_special_properties = {
        'publisher': (URIRef("https://w3id.org/idsa/core/Agent"), URIRef("https://w3id.org/idsa/core/publisher")),
        'license': (URIRef("http://purl.org/dc/terms/licence"), URIRef("https://w3id.org/idsa/core/standardLicense")),
        "location": (URIRef("https://w3id.org/idsa/core/Location"), URIRef("https://w3id.org/idsa/core/physicalLocation")),
        "language": (URIRef("http://purl.org/dc/terms/language"), URIRef("https://w3id.org/idsa/core/Language")),
        "domains": (URIRef("http://www.w3.org/ns/dcat#keyword"), URIRef("http://www.w3.org/ns/dcat#keyword"))
    }

    black_list_properties = ["contactPointIsAuthor"]
    # domains

    direct_map = {
        "formats": URIRef("http://www.w3.org/ns/dcat#mediaType"),
        "uploadTime": URIRef("http://www.w3.org/ns/dcat#startDate"),
    }
    special_values_map = dict()

    def __init__(self, uri_ontology, uri_or_path, database_conector, parse_format, writing_graph):
        # Create a Graph.
        # Graph used to save the ontology
        super().__init__(uri_ontology, uri_or_path,
                         database_conector, parse_format, writing_graph)


    def get_all_properties_of_class_witch_cache(self, prediction_class):
        """
        Retrieves all properties of a given class from cache or database.

        Args:
            prediction_class (str): The name of the prediction class.
            dict_ontology_access (dict): A dictionary containing ontology access information.

        Returns:
            tuple: A tuple containing two lists: the datatype property list and the object property list.
        """
        # Log the start of the function
        application_logger.info(f"Getting all properties for {str(prediction_class)}")

        # Initialize the lists to store properties
        datatype_property_list = []
        object_property_list = []

        try:
            # Check if the properties are already in cache
            datatype_property_list = db_cache.get_class_datatype_properties(prediction_class)
            object_property_list = db_cache.get_class_objecttype_properties(prediction_class)

            # If the properties are not in cache, retrieve them from the database
            if not datatype_property_list and not object_property_list:
                application_logger.info(f"There is no cache for {str(prediction_class)}")

                # Retrieve properties from the ontology
                datatype_property_list, object_property_list = self.get_all_type_properties_from_class(prediction_class)

                # Add the properties to cache
                if datatype_property_list:
                    db_cache.add_new_datatypes_class(prediction_class, datatype_property_list)
                if object_property_list:
                    db_cache.add_new_objectype_class(prediction_class, object_property_list)
            else:
                application_logger.warning(f"There are properties in cache for {str(prediction_class)}")
        except Exception as e:
            # Log any exceptions that occur
            application_logger.error(f"Exception caught, error in (__get_all_properties_of_class): {str(e)}")
            application_logger.error(e, exc_info=True)

        # Return the property lists
        return datatype_property_list, object_property_list

    def get_all_type_properties_from_class(self, class_uri):
        """
        Get all the datatype and object properties from a given class URI.
        
        Args:
            class_uri (str): The URI of the class.
        
        Returns:
            tuple: A tuple containing two lists. The first list contains the datatype properties and the second list 
            contains the object properties.
        """
        # Get the datatype properties
        datatype_property_list = self.object_dcat_list

        # Get the object properties
        object_property_list = self.object_dcat_list
        
        # Log a warning message
        application_logger.warning(f"DCAT has found all its properties!")

        # Return the two lists
        return datatype_property_list, object_property_list

    def mapping_metadata_to_class(self, metadata_list, class_query,  property_query=config.NODE_PROPERTY_NAME, uri_token=False, individual_uri=None, matchandmap=None, search_index=None):
        """
        Mapping between metadata properties and a ontology class properties.
        :param metadata_list: The list of metadata properties.
        :param uri_token: Boolean used to know if this functions is called recursively
        :param indiviual_uri: URI of an already created instance.
        :param class_query: The class used to find the proper class URI in the ontology.
        """
        application_logger.warning("Using DCAT functions!")
        class_uri = URIRef("http://www.w3.org/ns/dcat#Dataset")
        uri_list_result = list()
        if class_uri:
            application_logger.info(f"DCAT and its own properties!, Found class: {str(class_uri)}")

            datatype_property_list, object_property_list = self.get_all_properties_of_class_witch_cache(class_uri)

            # Instance class properties (Datatype and Object properties):
            for metadata_map in metadata_list:
                # Instance class by each metadata map:
                # Create an individual.
                if not uri_token:
                    class_name_str = self.get_class_name_from_uriref_str(
                        utils.get_uriref_str(class_uri))
                    individual_uri =self.generate_auxiliar_uri(ontology_uri=self.ONTOLOGY_URI, class_range_str=class_name_str)
                else:
                    # In case there is an uri already found for this new instance
                    uri_token = False

                application_logger.info(
                    "Finding if this URI already exists on the database...")

                found_uri_instance, current_uri = self.find_metadata_in_graph(
                    class_uri, metadata_map, property_query)
                application_logger.info(current_uri)

                if not found_uri_instance:
                    application_logger.info(
                        "No previous instance found, adding new instance...")
                    # Specify the class type of the individual.
                    self.add_new_triplet(individual_uri, RDF.type, class_uri)
                    uri_list_result.append(utils.get_uriref_str(individual_uri))

                else:
                    application_logger.warning(
                        "Updating the node, it already exists")
                    individual_uri = URIRef(current_uri)
                    uri_list_result.append(utils.get_uriref_str(current_uri))
                    self.add_new_triplet(individual_uri, RDF.type, class_uri)

                # List which gathers the values related to a key
                value_list = []
                application_logger.info(
                    "Adding metadata to the instance class...")
                # Add information related to Datatype properties or Object properties.
                application_logger.warning(metadata_map)
                for key, value_metadata in metadata_map.items():
                    object_property = None
                    datatype_property = None
                    similarity = 0
                    dict_ontology = db_cache.get_map_metadata(key)
                    # Value could be a list
                    # It is possible to have something like this:
                    # Key: language
                    # Value:  [{'resource': 'http://publications.europa.eu/resource/authority/language/ENG', 'id': 'en', 'label': 'English'}]
                    if not (value_metadata is None):
                        if not type(value_metadata) is list:
                            # In case value is not a list, it is required used it in a list in other
                            # to loop through its values
                            # The reason for having a loop is because it is possible to have lists as value for the keys in the dict
                            if (type(value_metadata) is str) and (";" in value_metadata):
                                value_list = utils.prepare_and_parse_ckan(
                                    value_metadata)
                            else:
                                value_list = [value_metadata]
                        else:
                            value_list = value_metadata
                        # Try to search the key for all the values linked to it
                        # In case it could not find the object property but the value is a dictionary
                        # it has to find the closet object property
                        for value in value_list:
                            # Check if it is an object property
                            # In case it is  an object property
                            if type(value) is dict:
                                application_logger.info(f"Adding Object... -> {str(key)}: {value}")
                                if dict_ontology:
                                    object_property = dict_ontology.get('property')
                                    similarity = dict_ontology.get('similarity')
                                else:
                                    application_logger.info("No previous objectype in cache...")
                                    object_property, range_property, similarity = self.search_sim_key_object_property_list(key, object_property_list, self.sim_threshold_property)
                                # create a relation between it an its range class
                                # second invoke this same function with its range class and the value, which should be a
                                # dictionary
                                if object_property:
                                    application_logger.info(f"Object {str(key)} ------ {str(object_property)}")
                                    db_cache.add_new_map_metadata(
                                        key, {'property': object_property, 'similarity': similarity})

                                    aux_list = self.__mapping_range_class(
                                        range_property, individual_uri, object_property, value, property_query, uri_list_result,  matchandmap=matchandmap, search_index=search_index)
                                    uri_list_result = uri_list_result + aux_list
                                else:
                                    application_logger.warning(f"No object property found: {str(key)}")

                            else:
                                application_logger.info(f"Adding Data... -> {str(key)}: {str(value)}")
                                # Check if the property is a property which have to be imported as a node
                                bool_created_property = False
                                if self.dict_special_properties.get(key):
                                    self.special_values_map[key] = value
                                    bool_created_property = True

                                if not bool_created_property:
                                    # In case it is not, check if it is a datatype property
                                    if dict_ontology:
                                        datatype_property = dict_ontology.get(
                                            'property')
                                        similarity = dict_ontology.get(
                                            'similarity')
                                    else:
                                        application_logger.info("No previous datatype in cache...")

                                        if self.direct_map.get(key):
                                            datatype_property = self.direct_map.get(
                                                key)
                                            similarity = 1
                                        elif (config.PROPERTY_TITLE not in key) and (key not in self.black_list_properties):
                                            datatype_property, similarity = self.search_sim_key_datatype_property_list(
                                                key, datatype_property_list, self.sim_threshold_property)
                                        elif (config.PROPERTY_TITLE not in key) and (key in self.black_list_properties):
                                            application_logger.info(
                                                "Property it is going to fail if it is mapped")
                                        else:
                                            datatype_property = DCTERMS.title
                                            similarity = 1
                                            self.add_new_triplet(
                                                utils.set_uriref_str(individual_uri), config.NODE_PROPERTY_NAME, Literal(value))

                                    if datatype_property:
                                        application_logger.info(
                                            f"Data: {str(key)} ------ {str(datatype_property)}")
                                        if config.PROPERTY_DESCRIPTION in key:
                                            if matchandmap and value:
                                                application_logger.info(
                                                    "Let's try to link its information...")
                                                try:
                                                    matchandmap.link_nodes_to_dataset(
                                                        individual_uri, value, self)
                                                except Exception as e:
                                                    application_logger.error(
                                                        "Error while enriching content...")
                                                    application_logger.error(e, exc_info=True)
                                        db_cache.add_new_map_metadata(
                                            key, {'property': datatype_property, 'similarity': similarity})

                                        self.add_new_triplet(
                                            utils.set_uriref_str(individual_uri), utils.set_uriref_str(datatype_property), Literal(value))
                                    else:
                                        application_logger.warning(
                                            f"No datatype property found: {str(key)}")
                                        datatype_property = str(
                                            "http://purl.org/dc/terms/"+str(key))
                                        application_logger.warning(
                                            f"We do not want to lose information, then the property {datatype_property} is about to be invented:")
                                        self.add_new_triplet(utils.set_uriref_str(individual_uri), utils.set_uriref_str(
                                            datatype_property), Literal(value))
                                        db_cache.add_new_map_metadata(
                                            key, {'property': utils.set_uriref_str(datatype_property), 'similarity': 1})
                ########################################################################################################
                application_logger.info(
                    f"Let's create the special properties for this dataset")
                pool_secondary = ThreadPool(len(self.special_values_map))
                for key, value in self.special_values_map.items():
                    try:
                        pool_secondary.apply_async(self.special_property_insert,
                                                   args=(key, value, individual_uri, search_index, matchandmap, ))
                    except Exception as e:
                        application_logger.error(
                            "Error while enriching content...")
                        application_logger.error(e, exc_info=True)
                pool_secondary.close()
                pool_secondary.join()
                self.save_graph_in_rdf_format()
                application_logger.info(f"Next dataset!")

        else:
            application_logger.error("No URIref found for " + str(class_query))
        return uri_list_result

    # Property query required because it is mapping an specific class
    def __mapping_range_class(self, range_uri, individual_uri, object_property, value, property_query, uri_list,  matchandmap=None, search_index=None):
        """
        Auxiliary function to :function mapping_metadata_to_class
        It is used to add a new triplet at the graph:
        <individual_uri> <object_property> <auxiliar_uri>

        :param range_uri: Uri of the classes linked by rdfs:range
        <class of "indiviual_uri"> <rdfs:range> <range_uri>
        :param individual_uri: Uri of the instances which is the object of the triplet
        :param object_property: Linking property between "individual_uri" auxiliar_uri
        :param value: Belonged value to the key "individual_uri"

        """
        # Specify the class type of the individual.
        found_uri_instance, current_uri = self.find_metadata_in_graph(
            range_uri, value, property_query)
        class_range_str = self.get_class_name_from_uriref_str(
            utils.get_uriref_str(range_uri))
        if not found_uri_instance:
            auxiliar_uri =self.generate_auxiliar_uri(ontology_uri=self.ONTOLOGY_URI, class_range_str=class_range_str)
            uri_list.append(utils.get_uriref_str(auxiliar_uri))
        else:
            application_logger.warning("Updating the node, it already exists")
            uri_list.append(utils.get_uriref_str(current_uri))
            auxiliar_uri = utils.set_uriref_str(current_uri)
        self.add_new_triplet(utils.set_uriref_str(individual_uri), utils.set_uriref_str(
            object_property), utils.set_uriref_str(auxiliar_uri))
        new_uri_list_result = self.mapping_metadata_to_class(
            [value], class_range_str,  property_query, uri_token=True, individual_uri=auxiliar_uri, matchandmap=matchandmap, search_index=search_index)
        return uri_list + new_uri_list_result
    
    def map_just_one_concept_to_node(self, primary_node, query, search_index_class, special_relation, matchandmap, language='en'):
        """
        Maps just one concept to a node in the ontology graph.

        Args:
        - primary_node: The URI of the primary node to map the concept to.
        - query: The concept query to be mapped.
        - search_index_class: The search index class for querying the ontology graph.
        - special_relation: The special relation to be added between the primary node and the concept node.
        - matchandmap: The match and map instance for searching and mapping the concept.
        - language: The language for the query (default is 'en').

        Returns:
        - head_instance_uri: The URI of the mapped concept instance.
        - head_prediction_class: The class of the mapped concept instance.
        """
        head_instance_uri = None  # Initialize head_instance_uri
        populate_list = list()  # Initialize populate_list

        try:
            # Search for the instance and class for the query
            matchandmap.map.main_ontology = self
            head_prediction_class, head_instance_uri, populating_ontology = matchandmap.map.search_instance_and_class_for_query(query, search_index_class, language)

            if head_instance_uri:
                # Add a new triplet between the primary node and the concept node
                self.add_new_triplet(URIRef(primary_node), URIRef(special_relation), URIRef(head_instance_uri))

                # Create content for populating the concept node
                populate_list = matchandmap.map.create_content_for_populating(
                    head_instance_uri, query, populate_list)

                # Update the search index with the populated content
                search_index_class.update_elastic_search_index_consulting(
                    populate_list)
        except Exception as e:
            # Log the error message and details
            error_message=f"""
            Error while mapping just one concept to node.
            primary_node: {str(primary_node)}
            query: {str(query)}
            search_index_class: {str(search_index_class)}
            special_relation: {str(special_relation)}
            language: {str(language)}
            Error: {str(e)}
            """
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)

        return head_instance_uri, head_prediction_class  # Return the mapped concept instance URI and class
    


    def special_property_insert(self, name_property, value, individual_uri, search_index_class, matchandmap=None):
        """
        Insert a special property into the graph.

        Args:
            name_property (str): The name of the property.
            value (str): The value of the property.
            individual_uri (str): The URI of the individual.
            search_index_class (str): The class to use for search indexing.
            matchandmap (MatchAndMap, optional): The MatchAndMap instance to use. Defaults to None.
        """
        try:
            class_node, relationship_node = self.dict_special_properties.get(name_property)

            # If "domains" is in the name of the property
            if "domains" in name_property:
                application_logger.warning(f"Domains property: Value: {str(value)}")
                value_list = utils.prepare_and_parse_ckan(value)
                application_logger.warning(f"Domains property: Value List: {str(value_list)}")

                for sub_value in value_list:
                    sub_value = str(sub_value).strip().capitalize()
                    application_logger.warning(f"Domains property: Attempting to import {sub_value}: Relationship: {str(relationship_node)}")
                    head_instance_uri, class_node = self.map_just_one_concept_to_node(individual_uri, sub_value, search_index_class, relationship_node, matchandmap)
                    application_logger.warning(f"Subvalue: {str(value)}, Relationship: {str(relationship_node)} Class: {str(class_node)} Individual: {str(individual_uri)}")
                    self.create_property(
                        sub_value, class_node, individual_uri, relationship_node, matchandmap)
            else:
            # If there is a semicolon in the value
                application_logger.warning(f"Before creating property: {str(name_property)} Value: {str(value)}")

                if ";" in value:
                    value_list = utils.prepare_and_parse_ckan(value)
                    application_logger.warning(f"Value List: {str(value_list)}")
                    for sub_value in value_list:
                        sub_value = str(sub_value).strip().capitalize()
                        application_logger.warning(f"Subvalue: {str(sub_value)}, Relationship: {str(relationship_node)} Class: {str(class_node)} Individual: {str(individual_uri)}")
                        self.create_property(
                            sub_value, class_node, individual_uri, relationship_node, matchandmap)
                else:
                    application_logger.warning(f"Value: {str(value)}, Relationship: {str(relationship_node)} Class: {str(class_node)} Individual: {str(individual_uri)}")
                    self.create_property(
                        value.strip(), class_node, individual_uri, relationship_node, matchandmap)
                
            application_logger.warning("---------------------------------------------------------")
        except Exception as e:
            application_logger.error("Error while mapping specials properties")
            application_logger.error(f"{str(name_property)} <-> {str(value)}")
            application_logger.error(e, exc_info=True)

    def create_property(self, name, class_node, individual_uri, relationship, matchandmap=None):
        """
        Create a property node and add a triplet to the graph.

        Args:
            name (str): The name of the property.
            class_node (str): The class node for the property.
            individual_uri (str): The individual URI for the property.
            relationship (str): The relationship between the individual and the property.
            matchandmap (object, optional): An instance of the MatchAndMap class. Defaults to None.
        """
        try:
            # Log a message indicating that we are trying to find the best node
            application_logger.info("---> Trying to find the best node! <--- ")

            # Save the cache content URI and get the result
            uri_result = matchandmap.map.save_cache_content_uri(name, class_node, self)
            # Add a new triplet to the graph
            self.add_new_triplet(utils.set_uriref_str(individual_uri), utils.set_uriref_str(
                relationship), utils.set_uriref_str(uri_result))
        except Exception as e:
            error_message= f"""
            Error while creating a node for a property: {str(e)}
            {str(name)} <-> {str(class_node)} <-> {str(individual_uri)} <-> {str(relationship)}
            """
            # Log an error message if an exception occurs
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)
