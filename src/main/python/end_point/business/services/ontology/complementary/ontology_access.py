
import uuid
import subprocess
import threading
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS
from end_point.business import utils
from end_point.business.services.search_services.sparql_query import SparqlQuery
from end_point.logging_ita import application_logger
import end_point.config as config
from end_point.config import db_cache
import os
# DATA VISUALIZATION
# https://medium.com/neo4j/tagged/data-visualization
# https://github.com/Nhogs/popoto
# https://github.com/neo4j-labs/rdflib-neo4j
# DCAT without dcterms
# https://github.com/w3c/dxwg/tree/gh-pages/dcat/rdf


class OntologyAccess:
    """
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

    def __init__(self, uri_ontology, uri_or_path, database_conector, parse_format, writing_graph):
        # Mutex for dealing with multithread
        self.mutex = threading.Lock()
        self.updating_ontology_mutex = threading.Lock()
        # Create a Graph.
        # Graph used to save the ontology
        self.graph = Graph()
        self.ONTOLOGY_URI = uri_ontology
        # Graph used to write the new triplets
        self.writing_graph = writing_graph
        self.bind_namespace_graph()
        # Parse in an RDF file hosted on the Internet.
        # Documentation:
        # https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html
        # turtle, rdf/xml, n3, n-triples, trix, JSON-LD, etc
        self.graph.parse(uri_or_path, format=parse_format)
        self.base_resource_path = config.APP_ONTOLOGY

        # set the configuration to connect to your Neo4j DB
        self.database = database_conector

        self.sparql = SparqlQuery(self.graph, uri_ontology)
        self.writing_sparql = SparqlQuery(writing_graph, uri_ontology)

        # Entities start with 'all_':
        self.all_classes = self.get_all_classes()
        self.all_properties = self.get_all_properties()
        self.all_properties_annotation = self.get_all_properties_annotation()
        self.all_properties_object = self.get_all_properties_object()
        self.all_properties_datatype = self.get_all_properties_datatype()
        self.all_named_individuals = self.get_all_named_individual()

        self.sim_threshold_main_property = 0.95
        self.sim_threshold_property = 0.75

    def generate_auxiliar_uri(self, ontology_uri, class_range_str):
        """
        Generate an auxiliary URI based on the ontology URI and class range string.

        Args:
            ontology_uri (str): The ontology URI.
            class_range_str (str): The class range string.

        Returns:
            str: The generated auxiliary URI.
        """
        return URIRef(ontology_uri + '#' + class_range_str.replace(" ", "_") + '_' + str(uuid.uuid4()))


    def bind_namespace_graph(self):
        """
        Binds the namespaces to the graph and the writing graph.
        """
        # Get the dictionary of prefix namespaces from the configuration
        dict_prefix_namespaces = config.ONTOLOGY_PREFIX
        
        # Iterate over each prefix and namespace in the dictionary
        for prefix, namespace in dict_prefix_namespaces.items():
            # Bind the prefix and namespace to the graph
            self.graph.bind(prefix, namespace)
            
            # Bind the prefix and namespace to the writing graph
            self.writing_graph.bind(prefix, namespace)

    def add_new_triplet(self, subject, predicate, object):
        """Auxiliary function to add a new triplet to the graph:
        <subject> <predicate> <object>

        Args:
            subject ([URIRef]):
            predicate ([URIRef]):
            object ([URIRef or Literal]):
        """
        self.mutex.acquire()
        try:
            self.writing_graph.add((subject, predicate, object))
            # current date and time
            application_logger.info(
                f"Triplet added: {str(subject)} --> {str(predicate)} --> {str(object)}")
        except Exception as e:
            application_logger.error(
                f'Exception caught while trying to add a normal triplet (add_new_triplet): {str(e)}')
            application_logger.error(
                f"Failed triplet: {str(subject)} --> {str(predicate)} --> {str(object)}")
            application_logger.error(e, exc_info=True)
        self.mutex.release()

    def add_alternative_title_triplet(self, uri_triplet, second_title):
        """
        Adds an alternative title triplet to the RDF graph.

        Args:
            uri_triplet (str): The URI of the triplet.
            second_title (str): The alternative title to add.

        Returns:
            None
        """
        try:
            # Log the action of adding an alternative title
            application_logger.info("Adding an alternative title...")

            # Add the new triplet to the RDF graph
            self.add_new_triplet(
                utils.set_uriref_str(uri_triplet), DCTERMS.alternative, Literal(second_title))
        except Exception as e:
            # Log any errors that occur
            error_message=f"""
            Error while adding alternative title
            URI Triplet: {str(uri_triplet)}
            Second Title: {str(second_title)}
            Error: {str(e)}
            """
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)

    def add_new_datatype_triplet(self, head, head_class):
        """Add a new triplet with the following structure:
        <Subject> <Datatype property> <Object>
        In the new triplet the predicate is a datatype property.

        Args:
            head (string): Content to be added as <Object>
            head_class (URIRef(string)): Class of the <Subject>
        """

        # Creates an URI for the new instance of the class
        individual_uri = None
        application_logger.info(
            f'Creating a new URI for the class: {head_class}')
        try:
            class_name_str = self.get_class_name_from_uriref_str(head_class)
            individual_uri = self.generate_auxiliar_uri(ontology_uri=self.ONTOLOGY_URI, class_range_str=class_name_str)
            # Specify the class type of the individual.
            self.add_new_triplet(utils.set_uriref_str(
                individual_uri), RDF.type, utils.set_uriref_str(head_class))
            self.add_new_triplet(
                utils.set_uriref_str(individual_uri), config.NODE_PROPERTY_NAME, Literal(head))

            application_logger.info(f'URI: {individual_uri}')
        except Exception as e:
            error_message = f"""
            Error while adding new datatype triplet
            Triplet head: {str(head)}
            Head Class: {str(head_class)}
            Individual URI: {str(individual_uri)}
            Error: {str(e)}
            """
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)

        return individual_uri


    def get_all_attributes_instance(self, uri_individual):
        """Get all the instance of a class

        Args:
            uri_individual (URIRef()): URI which identifies a class

        Returns:
            list: List which contain all the instances of the given class
        """
        properties_list = list()
        for subj, pred, obj in self.graph:
            if subj == uri_individual:
                properties_list.append((subj, pred, obj))

        return properties_list

    def get_all_classes(self, class_predicate='', remove_blank_nodes=True):
        """  
        Extracts all classes of a graph (or ontology).      
        :param class_predicate: The predicate class (default='').
        :param remove_blank_nodes: If to remove blanc nodes (default=True)
        :return: All the classes from an ontology.        
        """
        exit = []
        if not class_predicate:
            for s, v, o in self.graph.triples((None, RDF.type, OWL.Class)):
                exit.append(s)
            for s, v, o in self.graph.triples((None, RDF.type, RDFS.Class)):
                exit.append(s)
            # This extra routine makes sure we include classes not declared explicitly.
            # eg., when importing another ontology and subclassing one of its classes.
            for s, v, o in self.graph.triples((None, RDFS.subClassOf, None)):
                if s not in exit:
                    exit.append(s)
                if o not in exit:
                    exit.append(o)
            # This extra routine includes classes found only in rdfs:domain and rdfs:range definitions.
            for s, v, o in self.graph.triples((None, RDFS.domain, None)):
                if o not in exit:
                    exit.append(o)
            for s, v, o in self.graph.triples((None, RDFS.range, None)):
                if o not in exit:
                    exit.append(o)
        else:
            if class_predicate == "rdfs" or class_predicate == "rdf":
                for s, v, o in self.graph.triples((None, RDF.type, RDFS.Class)):
                    exit.append(s)
            elif class_predicate == "owl":
                for s, v, o in self.graph.triples((None, RDF.type, OWL.Class)):
                    exit.append(s)
            else:
                raise Exception(
                    "ClassPredicate must be either rdf, rdfs or owl")
        exit = self.remove_duplicates(exit)
        if remove_blank_nodes:
            exit = [x for x in exit if not self.is_blank_node(x)]
        return self.sort_uri_list_by_name(exit)

    def get_all_properties(self, hide_implicit_preds=True):
        """
        Get all properties of a graph (or ontology): rdf:Property, owl:ObjectProperty, owl:DatatypeProperty and owl:AnnotationProperty
        :param hide_implicit_preds: If hide predicates (default=True).
        :return: All properties of a graph.
        """
        return self.sparql.get_all_properties(hide_implicit_preds)

    def get_all_properties_by_query(self, query):
        """
        Get properties of a graph (or ontology) according to the query
        :return: Properties of a graph List
        """
        property_list = list()
        for prop_value, prop_type, prop_range in self.all_properties:
            if prop_type.toPython() == query:
                property_list.append((prop_value, prop_type, prop_range))
        return property_list

    def get_all_properties_annotation(self):
        """
        Get annotation properties of a graph (or ontology): owl:AnnotationProperty        
        :return: Annotation properties of a graph. 
        """
        return self.get_all_properties_by_query(str(OWL.AnnotationProperty))

    def get_all_properties_object(self):
        """
        Get object properties of a graph (or ontology): owl:ObjectProperty        
        :return: Object properties of a graph. 
        """
        return self.get_all_properties_by_query(str(OWL.ObjectProperty))

    def get_all_properties_datatype(self):
        """
        Get data properties of a graph (or ontology): owl:DatatypeProperty        
        :return: Datatype properties of a graph. 
        """
        return self.get_all_properties_by_query(str(OWL.DatatypeProperty))

    def get_all_named_individual(self):
        """
        Get named individual properties of a graph (or ontology): owl:NamedIndividual        
        :return: Named individual properties of a graph. 
        """
        return self.get_all_properties_by_query(str(OWL.NamedIndividual))

    def get_all_properties_from_class(self, class_object):
        """
        Get all properties from a specific class.
        Example of triplet: 
        <subject> <predicate> <object>
        <https://w3id.org/idsa/core/description> <http://www.w3.org/2000/01/rdf-schema#domain> <https://w3id.org/idsa/core/Described>
        :param class_name: The class name: eg., URIRef('https://w3id.org/idsa/core/Described')
        :return: All properties from a specific class.
        """
        datatype_property_list = list()
        for subj, pred, obj in self.graph:
            if pred == RDFS.domain and obj == class_object:
                datatype_property_list.append(subj)
        return datatype_property_list

    def get_all_properties_objectype_from_class(self, class_object):
        """
        Get all Object properties from a specific class.
        Example of triplet: 
        <subject> <predicate> <object>
        <https://w3id.org/idsa/core/description> <http://www.w3.org/2000/01/rdf-schema#domain> <https://w3id.org/idsa/core/Described>
        :param class_name: The class name: eg., URIRef('https://w3id.org/idsa/core/Described')
        :return: All object properties from a specific class.
        """
        objectype_property_list = list()
        for subj, pred, obj in self.graph:
            if pred == RDFS.domain and obj == class_object:
                for prop_value, prop_type, prop_range in self.all_properties_object:
                    if subj == prop_value:
                        objectype_property_list.append(
                            (prop_value, prop_type, prop_range))
        return objectype_property_list

    def get_all_namespaces(self):
        """
        Get all namespaces of the ontology.
        :return: All ontology namespaces.
        """
        return self.graph.namespaces()


    def get_class_direct_subs(self, class_object, exclude_bnodes=True):
        """
        Get only direct sub-classes of a specific class, excluding blank nodes.
        :param class_object: The specific class.
        :param exclude_bnodes: If exclude the blank nodes (default=True).
        :return: A list of direct sub-classes of a specific class.
        """
        sub_class_list = []
        for s, v, o in self.graph.triples((None, RDFS.subClassOf, class_object)):
            if exclude_bnodes:
                if not self.is_blank_node(s):
                    sub_class_list.append(s)
            else:
                sub_class_list.append(s)
        return self.sort_uri_list_by_name(self.remove_duplicates(sub_class_list))

    def get_class_all_subs(self, class_object, return_list=[], exclude_bnodes=True):
        """
        Get all sub-classes of a specific class, excluding blank nodes.
        :param class_object: The specific class.
        :param return_list: List used recursively to store sub-classes. 
        :param exclude_bnodes: If exclude the blank nodes (default=True).
        :return: A list with all sub-classes of a specific class.
        """
        for sub in self.get_class_direct_subs(class_object, exclude_bnodes):
            return_list.append(sub)
            self.get_class_all_subs(sub, return_list, exclude_bnodes)
        return self.sort_uri_list_by_name(self.remove_duplicates(return_list))


    def sort_uri_list_by_name(self, uri_list, bypass_namespace=False):
        """
        Sorts a list of URIs.
        :param uri_list: List of URIs.
        :param bypass_namespace: It checks whether the last bit is specified using a '#' or just a '/' (default=False).        
                                 eg., rdflib.URIRef('http://purl.org/ontology/mo/Vinyl') or rdflib.URIRef('http://purl.org/vocab/frbr/core#Work')
        :return: A sorted URI list.                                 
        """
        def get_last_bit(uri_string):
            try:
                x = uri_string.split("#")[1]
            except:
                x = uri_string.split("/")[-1]
            return x
        try:
            if bypass_namespace:
                return sorted(uri_list, key=lambda x: get_last_bit(x.__str__()))
            else:
                return sorted(uri_list)
        except Exception as e:
            application_logger.warning("Error in <sort_uri_list_by_name>: possibly a UnicodeEncodeError")
            application_logger.error(e, exc_info=True)
        return uri_list

    def remove_duplicates(self, seq, idfun=None):
        """ 
        Removes duplicates from a list, order preserving, as found in: http://www.peterbe.com/plog/uniqifiers-benchmark
        :param seq: A element list.
        :param idfun: The id fun ¿?
        :return: A list without duplicate elements.
        """
        # order preserving
        if idfun is None:
            def idfun(x):
                return x
        seen = {}
        result = []
        for item in seq:
            marker = idfun(item)
            # in old Python versions:
            # if seen.has_key(marker)
            # but in new ones:
            if marker in seen:
                continue
            seen[marker] = 1
            result.append(item)
        return result

    def is_blank_node(self, a_class):
        """ 
        Checks if a class is a blank node.
        :param a_class: The specified class.
        :return: True the class is a blank node, and False in otherwise.
        """
        if type(a_class) == BNode:
            return True
        else:
            return False


    def get_most_similar_class_uriref(self, query):
        """
        Get the Uriref of the class which has the most similar name to the query.
        :param query: The name of a class yet to find
        :return: Uriref of the classes whose name is the most similar to the query
        Eg: query = "Smart Data"
            return URIRef(https://w3id.org/idsa/core/SmartDataApp)
        """
        similar_class = None
        score = 0
        measure = config.semantic_search
        # Check if there are classes which contain the query as part of their name
        classes_to_test, list_get_all_classes = self.get_classes_from_text(
            query)
        # In case there is not classes, get them all
        if not classes_to_test:
            classes_to_test = list_get_all_classes

        # Dictionary name:uri to get quick access to the uri
        pair_name_uri = {}
        class_name_list = []
        application_logger.info(f"Searching for candidates to: {query}")
        for test_class in classes_to_test:
            uriref_str = utils.get_uriref_str(test_class)
            class_name = self.get_class_name_from_uriref_str(uriref_str)

            if not class_name:
                class_name = utils.get_name_from_url(uriref_str)
            # The class name may be compose by two words with are not separate
            # by spaces
            if class_name:
                # Separate the name by the words which compose it
                new_name = utils.transform_class_name(class_name)
                # TODO CAMBIAR EN EL FUTURO
                if not pair_name_uri.get(new_name):
                    class_name_list.append(new_name)
                    pair_name_uri[new_name] = uriref_str
                elif self.ONTOLOGY_URI in uriref_str:
                    class_name_list.append(new_name)
                    pair_name_uri[new_name] = uriref_str

        if class_name_list:
            candidate_id, score = measure.word_similarity_from_list(
                query, class_name_list)

            class_final_name = class_name_list[candidate_id]
            similar_class = utils.set_uriref_str(
                pair_name_uri[class_final_name])

        application_logger.info(f"Similar class found: {similar_class}")

        return similar_class, score

    def get_classes_from_text(self, text):
        """
        Get the saved-class with given class text.
        Eg:
            In [1]: g.get_class(match="person")
            Out[1]:
            [<Class *http://purl.org/ontology/bibo/PersonalCommunicationDocument*>,
             <Class *http://purl.org/ontology/bibo/PersonalCommunication*>,
             <Class *http://xmlns.com/foaf/0.1/Person*>]
        :param text: The text to match with URIs.
        :return: List of classes that matches with a text.
        """
        class_list = []
        if type(text) != type("string"):
            return []
        else:
            list_get_all_classes = self.all_classes
            for uriref in list_get_all_classes:
                uriref_str = utils.get_uriref_str(uriref)
                class_name = self.get_class_name_from_uriref_str(uriref_str)

                if (class_name) and (text.lower() in class_name.lower()):
                    class_list += [uriref]

        return class_list, list_get_all_classes

    def get_class_name_from_uriref_str(self, uriref_str):
        """
        Get the class name from a URIref.
        :param uriref: The URIref.
        :return: The class name.
        """
        class_name = ''
        for namespace in self.get_all_namespaces():
            if namespace[1] in uriref_str:
                class_name = uriref_str.replace(namespace[1], '')
                class_name = class_name.replace('#', '')
                class_name = class_name.replace('/', '')
        if class_name == '' or not class_name:
            class_name = utils.delete_ontology_preffix(uriref_str)
        return class_name

    def get_all_type_properties_from_class(self, class_uri):
        """Get all datatype and objectype properties of a class

        Args:
            class_uri (URIRef): URI of a class
        """
        application_logger.info(f"Getting all properties of {str(class_uri)}")

        datatype_property_list = self.get_all_properties_from_class(class_uri)
        object_property_list = self.get_all_properties_objectype_from_class(
            class_uri)
        application_logger.info(f"Properties extracted!")
        return datatype_property_list, object_property_list


    def get_all_properties_of_class_witch_cache(self, prediction_class):
        """
        Retrieves all properties of a given prediction class from the cache or the database.

        Args:
            prediction_class (str): The prediction class to retrieve properties for.
            dict_ontology_access (dict): A dictionary containing ontology access information.

        Returns:
            tuple: A tuple containing two lists of properties: datatype_property_list and object_property_list.
        """
        # Log the start of the function
        application_logger.info(f"Getting all properties for {str(prediction_class)}")
        # Initialize the property lists
        datatype_property_list = []
        object_property_list = []

        try:
            # Try to retrieve properties from the cache
            datatype_property_list = db_cache.get_class_datatype_properties(prediction_class)
            object_property_list = db_cache.get_class_objecttype_properties(prediction_class)

            # If there are no properties in the cache
            if not datatype_property_list and not object_property_list:
                application_logger.info(f"There is no cache for {str(prediction_class)}")

                # Call a method to retrieve properties from the database
                datatype_property_list, object_property_list = self.get_all_type_properties_from_class(prediction_class)
                # If there are datatype properties, add them to the cache
                if datatype_property_list:
                    db_cache.add_new_datatypes_class(prediction_class, datatype_property_list)

                # If there are object properties, add them to the cache
                if object_property_list:
                    db_cache.add_new_objectype_class(prediction_class, object_property_list)
            else:
                application_logger.warning(f"There are properties in cache for {str(prediction_class)}")
        except Exception as e:
            application_logger.error(f"Exception caught, error in (__get_all_properties_of_class): {str(e)}")
            application_logger.error(e, exc_info=True)

        # Return the property lists
        return datatype_property_list, object_property_list

    def is_http(self, text):
        """
        Checks if the string text is in HTML format.
        :param text: The string text.
        :return: True if the text is in HTML format, and False in otherwise.
        """
        if text:
            if text.startswith("http://") or text.startswith("https://"):
                return True
        return False

    def write_result_list_to_file(self, result_list, file_path):
        f = open(file_path, "w")
        for element in result_list:
            f.write('\n' + str(element))
        f.close()
        return file_path

    def save_graph_in_rdf_format(self):
        """
        Get the entire graph in a specific format (default='turtle'). 
        There are different type of formats: format='turtle', format="json-ld", format='nt', format="pretty-xml", format='n3'
        :param format: The type of format.
        :return:
        """
        self.updating_ontology_mutex.acquire()
        try:
            self.__save_graph_database(
                self.writing_graph, config.UPDATED_ONTOLOGY_FILE_NAME, bool_import=True)
            self.writing_graph = Graph()
        except Exception as e:
            application_logger.error(e, exc_info=True)
        self.updating_ontology_mutex.release()

    def search_key_in_object_property_list(self, key, objectype_property_list):
        """
        Search if a object property exists in a given list and return its rdfs:range
        :param key: Name of a property to be found in the object property list
        :param objectype_property_list: List which contains object properties
        :return: The object property and its rdfs:range 
        """
        object_property = None
        object_range = None
        if ':' in key:
            key = key.split(':')[1]
        for prop_value, prop_type, prop_range in objectype_property_list:
            object_property_str = self.get_class_name_from_uriref_str(
                prop_value)
            if object_property_str == key:
                object_property = prop_value
                object_range = prop_range
                break
        return object_property, object_range

    def search_key_in_datatype_property_list(self, key, datatype_property_list):
        """
        Search a metadata key in a list of datatype properties of the graph (or ontology).
        :param key: The metadata key (or property, attribute, etc.).
        :param datatype_property_list: The list of datatype properties of the graph (or ontology).
        :return: The Datatype property found in the graph.
        """
        datatype_property = None
        if ':' in key:
            key = key.split(':')[1]
        for datatype_property_uriref in datatype_property_list:
            datatype_property_str = self.get_class_name_from_uriref_str(
                datatype_property_uriref)

            if datatype_property_str == key:
                datatype_property = datatype_property_uriref
                break
        return datatype_property

    def __aux_compare_key_properties(self, property, word1, word2):
        """
        Compare the key properties of two words.

        Args:
            property (str): The property to compare.
            word1 (str): The first word.
            word2 (str): The second word.

        Returns:
            tuple: A tuple containing the object property and the semantic similarity score.
        """
        object_property = None

        # Get the metadata dictionary for word1 from the database cache
        dict_ontology = db_cache.get_map_metadata(word1)

        if dict_ontology:
            # Retrieve the object property and semantic similarity score from the dictionary
            object_property = dict_ontology.get('property')
            semantic_similarity = dict_ontology.get('similarity')
        else:
            # Calculate the semantic similarity score using the syns_maker module
            semantic_similarity = config.syns_maker.semantic_english_score(
                word1, word2)
            object_property = property

        return object_property, semantic_similarity

    def search_sim_key_object_property_list(self, key, objectype_property_list, min_threshhold):
        """
        Search the object property of the graph (or ontology) most similar to a metadata property (key).
        :param key: The metadata key (or property, attribute, etc.).
        :param objectype_property_list: The list of datatype properties of the graph (or ontology).
        :return: The Object property most similar found in the graph and its rdf:range.
        """

        best_object_property = None
        best_object_range = None
        high_similarity = 0
        word1 = utils.transform_class_name(utils.get_uriref_str(key))
        application_logger.info(f"Applying semantic rules to {str(key)}")
        try:
            if objectype_property_list:
                for prop_value, prop_type, prop_range in objectype_property_list:
                    word2 = utils.transform_class_name(
                        utils.delete_ontology_preffix((utils.get_uriref_str(prop_value))))
                    object_property, similarity = self.__aux_compare_key_properties(
                        prop_value, word1, word2)
                    if object_property and similarity > high_similarity and similarity > min_threshhold:
                        high_similarity = similarity
                        best_object_property = object_property
                        best_object_range = prop_range
                        db_cache.add_new_map_metadata(
                            word1, {'property': object_property, 'similarity': high_similarity})
                    application_logger.info(f"{str(object_property)}")
        except Exception as e:
            error_message=f"""
            Error while searching for object property: {str(e)}
            Key: {str(key)}
            objectype_property_list: {str(objectype_property_list)}
            """
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)

        application_logger.info(
            f"Semantic Result -> {str(best_object_property)}, {str(best_object_range)}, {str(high_similarity)}")
        return best_object_property, best_object_range, high_similarity

    def search_sim_key_datatype_property_list(self, key, datatype_property_list, min_threshhold):
        """
        Search the datatype property of the graph (or ontology) most similar to a metadata property (key).
        :param key: The metadata key (or property, attribute, etc.).
        :param datatype_property_list: The list of datatype properties of the graph (or ontology).
        :return: The Datatype property most similar found in the graph.
        """
        best_datatype_property = None
        high_similarity = 0
        word1 = utils.transform_class_name(utils.get_uriref_str(key))
        application_logger.info(f"Applying semantic rules to {str(key)}")
        try:
            for datatype_property_uriref in datatype_property_list:
                word2 = utils.transform_class_name(utils.delete_ontology_preffix(
                    utils.get_uriref_str(datatype_property_uriref)))
                datatype_property, similarity = self.__aux_compare_key_properties(
                    datatype_property_uriref, word1, word2)
                if datatype_property and similarity > high_similarity and similarity > min_threshhold:
                    high_similarity = similarity
                    best_datatype_property = datatype_property
                    db_cache.add_new_map_metadata(
                        word1, {'property': datatype_property, 'similarity': high_similarity})
                # application_logger.info(f"{str(datatype_property)}")
        except Exception as e:
            error_message=f"""
            Error while searching for datatype property: {str(e)}
            Key: {str(key)}
            datatype_property_list: {str(datatype_property_list)}
            """
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)

        application_logger.info(f"Semantic Result -> {str(best_datatype_property)}, {str(high_similarity)}")
        return best_datatype_property, high_similarity

    # Property query required because it is mapping an specific class
    def __mapping_range_class(self, range_uri, individual_uri, object_property, value, property_query, uri_list, matchandmap=None):
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
            auxiliar_uri = self.generate_auxiliar_uri(ontology_uri=self.ONTOLOGY_URI, class_range_str=class_range_str)
            uri_list.append(utils.get_uriref_str(auxiliar_uri))
        else:
            application_logger.warning("Updating the node, it already exists")
            uri_list.append(utils.get_uriref_str(current_uri))
            auxiliar_uri = utils.set_uriref_str(current_uri)
        self.add_new_triplet(utils.set_uriref_str(individual_uri), utils.set_uriref_str(
            object_property), utils.set_uriref_str(auxiliar_uri))
        new_uri_list_result = self.mapping_metadata_to_class(
            [value], class_range_str, property_query, uri_token=True, individual_uri=auxiliar_uri, matchandmap=matchandmap)
        return uri_list + new_uri_list_result

    def mapping_metadata_to_class(self, metadata_list, class_query, property_query=config.NODE_PROPERTY_NAME, uri_token=False, individual_uri=None, matchandmap=None, search_index=None):
        """
        Mapping between metadata properties and a ontology class properties.         
        :param metadata_list: The list of metadata properties.
        :param uri_token: Boolean used to know if this functions is called recursively
        :param indiviual_uri: URI of an already created instance.
        :param class_query: The class used to find the proper class URI in the ontology.        
        """
        cache_prediction_class = db_cache.get_class_of_prediction(class_query)
        uri_list_result = list()
        if cache_prediction_class:
            class_uri = cache_prediction_class
        else:
            class_uri, class_score = self.get_most_similar_class_uriref(
                class_query)
            db_cache.add_new_prediction_class(class_query, class_uri)

        if class_uri:
            application_logger.info(f"Found class: {str(class_uri)}")
            datatype_property_list = list()
            object_property_list = list()
            try:
                datatype_property_list, object_property_list = self.get_all_properties_of_class_witch_cache(class_uri)
            except Exception as e:
                application_logger.error("No properties!")

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
                application_logger.info(f"URI FOUND: {str(current_uri)}")

                if not found_uri_instance:
                    application_logger.info(
                        "No previous instance found, adding new instance...")
                    # Specify the class type of the individual.
                    self.add_new_triplet(utils.set_uriref_str(
                        individual_uri), RDF.type, utils.set_uriref_str(class_uri))
                    uri_list_result.append(
                        utils.get_uriref_str(individual_uri))

                else:
                    application_logger.warning(
                        "Updating the node, it already exists")
                    individual_uri = utils.set_uriref_str(current_uri)
                    uri_list_result.append(utils.get_uriref_str(current_uri))

                # List which gathers the values related to a key
                value_list = []
                application_logger.info(
                    "Adding metadata to the instance class...")
                # Add information related to Datatype properties or Object properties.
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
                                application_logger.info(
                                    f"Adding Object... -> {str(key)}: {value}")
                                if dict_ontology:
                                    object_property = dict_ontology.get(
                                        'property')
                                    similarity = dict_ontology.get(
                                        'similarity')
                                else:
                                    application_logger.info(
                                        "No previous objectype in cache...")
                                    object_property, range_property, similarity = self.search_sim_key_object_property_list(
                                        key, object_property_list, self.sim_threshold_property)
                                # create a relation between it an its range class
                                # second invoke this same function with its range class and the value, which should be a
                                # dictionary
                                if object_property:
                                    application_logger.info(
                                        f"Object {str(key)} ------ {str(object_property)}")
                                    db_cache.add_new_map_metadata(
                                        key, {'property': object_property, 'similarity': similarity})

                                    aux_list = self.__mapping_range_class(
                                        range_property, individual_uri, object_property, value, property_query, uri_list_result, matchandmap=matchandmap)
                                    uri_list_result = uri_list_result + aux_list
                                else:
                                    application_logger.warning(
                                        f"No object property found: {str(key)}")

                            else:
                                application_logger.info(
                                    f"Adding Data... -> {str(key)}: {str(value)}")
                                # In case it is not, check if it is a datatype property
                                if dict_ontology:
                                    datatype_property = dict_ontology.get(
                                        'property')
                                    similarity = dict_ontology.get(
                                        'similarity')
                                else:
                                    application_logger.info(
                                        "No previous datatype in cache...")
                                    datatype_property, similarity = self.search_sim_key_datatype_property_list(
                                        key, datatype_property_list, self.sim_threshold_property)

                                if datatype_property:
                                    application_logger.info(
                                        f"Data {str(key)} ------ {str(datatype_property)}")
                                    if config.PROPERTY_DESCRIPTION in key:
                                        if matchandmap and value:
                                            application_logger.info(
                                                "Let's try to link its information...")
                                            try:
                                                matchandmap.link_nodes_to_dataset(
                                                    individual_uri, value, ontology_access=self)
                                            except Exception as e:
                                                application_logger.error(
                                                    "Error while enriching content...")
                                                application_logger.error(e, exc_info=True)
                                    db_cache.add_new_map_metadata(
                                        key, {'property': datatype_property, 'similarity': similarity})

                                    self.add_new_triplet(
                                        utils.set_uriref_str(individual_uri), utils.set_uriref_str(datatype_property), Literal(value))
                                    # TODO: Poner "break" para evitar redundancia (varias properties con la misma información porque son tb similares y cumplen con el umbral)
                                else:
                                    application_logger.warning(
                                        f"No datatype property found: {str(key)}")
                                    datatype_property = f"{str(self.ONTOLOGY_URI)}/{str(key)}"
                                    application_logger.warning(
                                        f"We do not want to lose information, then the property {datatype_property} is about to be invented:")
                                    self.add_new_triplet(utils.set_uriref_str(individual_uri), utils.set_uriref_str(
                                        datatype_property), Literal(value))
                                    db_cache.add_new_map_metadata(
                                        key, {'property': utils.set_uriref_str(datatype_property), 'similarity': 1})

                application_logger.warning(
                    f"Saving dataset!")
                self.save_graph_in_rdf_format()
        else:
            application_logger.error("No URIref found for " + str(class_query))
        return uri_list_result

    def add_new_datatype_to_ontology(self, property_uri, head_class, tail_content):
        """ Add a new owl:DatatypeProperty to the ontology or graph
        Triplet format:
        <subject> <predicate> <object>
        Both subject and object are classes which belong to an ontology
        Args:
            property_uri ([str]): URI of the predicate
            head_class ([str]): URI of the subject
            tail_class ([str]): URI of the object
        """

        tail_class = self.__get_schema_type(tail_content)
        property_uri = self.ONTOLOGY_URI + '/' + property_uri

        self.__add_new_property_to_ontology(self.writing_graph,
                                            property_uri, head_class, tail_class, OWL.DatatypeProperty)

        self.__add_new_property_to_ontology(self.graph,
                                            property_uri, head_class, tail_class, OWL.DatatypeProperty)
        db_cache.add_new_datatypes_class(property_uri, self.__update_propeties_list(
            db_cache.get_class_datatype_properties(head_class), property_uri))

        return utils.set_uriref_str(property_uri)

    def add_new_objecttype_to_ontology(self, property_uri, head_class, tail_class):
        """ Add a new owl:ObjectProperty to the ontology or graph
        Triplet format:
        <subject> <predicate> <object>
        Both subject and object are classes which belong to an ontology
        Args:
            property_uri ([str]): URI of the predicate
            head_class ([str]): URI of the subject
            tail_class ([str]): URI of the object
        """
        property_uri = self.ONTOLOGY_URI + '/' + property_uri
        self.__add_new_property_to_ontology(self.writing_graph,
                                            property_uri, head_class, tail_class, OWL.ObjectProperty)
        self.__add_new_property_to_ontology(self.graph,
                                            property_uri, head_class, tail_class, OWL.ObjectProperty)

        db_cache.add_new_objectype_class(property_uri, self.__update_propeties_list(
            db_cache.get_class_objecttype_properties(head_class), property_uri))

        return utils.set_uriref_str(property_uri)

    def __update_propeties_list(self, objectproperties, property_uri):
        """
        Update the list of object properties with a new property URI.

        Args:
            object_properties (list): The original list of object properties.
            property_uri (str): The URI of the new property to add.

        Returns:
            list: The updated list of object properties.
        """
        application_logger.info(f"Adding new property -> {str(property_uri)}")
        try:
            if not objectproperties or type(objectproperties) == None:
                objectproperties = list()
            objectproperties.append(property_uri)
        except Exception as e:
            application_logger.error(f"Somethin is wrong {str(e)}")
            application_logger.error(e, exc_info=True)
        return objectproperties

    def __add_new_property_to_ontology(self, selected_graph, property_uri, head_class, tail_class, propertytype):
        """
        Add a new property to the ontology.

        Args:
            selected_graph (Graph): The graph to which the property will be added.
            property_uri (str): The URI of the property.
            head_class (str): The URI of the domain class.
            tail_class (str): The URI of the range class.
            propertytype (str): The type of the property.

        """
        try:
            # Add property type
            selected_graph.add(
                (utils.set_uriref_str(property_uri), RDF.type, utils.set_uriref_str(propertytype)))
            # Add domain class
            selected_graph.add(
                (utils.set_uriref_str(property_uri), RDFS.domain, utils.set_uriref_str(head_class)))
            # Add range class
            selected_graph.add(
                (utils.set_uriref_str(property_uri), RDFS.range, utils.set_uriref_str(tail_class)))

        except Exception as e:
            application_logger.error(
                f'Exception caught while adding new property: {str(e)}')
            application_logger.error(
                f'Error in function (__add_new_property_to_ontology)')
            application_logger.error(e, exc_info=True)

    def __merge_with_main_ontology(self, secondary_graph):
        """
        Merges the secondary ontology graph with the main ontology graph.

        Args:
            secondary_graph (Graph): The secondary ontology graph.

        Raises:
            Exception: If there is an error while merging or saving the ontology.

        """
        try:
            # Load the main ontology graph
            graph_2 = Graph()
            application_logger.info("Merging old ontology with the new one...")
            graph_2.parse(config.EXTENDED_IDS_ONTOLOGY_PATH)

            # Set appropriate permissions for ontology file
            subprocess.call(['chmod', '0777', config.EXTENDED_IDS_ONTOLOGY_PATH])

            # Merge the secondary graph with the main graph
            graph_1 = secondary_graph + graph_2

            # Save the merged graph to the ontology file
            application_logger.info("Saving new ontology file...")
            graph_1.serialize(
                destination=config.EXTENDED_IDS_ONTOLOGY_PATH,
                format=config.IDS_CORE_FORMAT_LOW_CHARACTERS,
                encoding='utf-8'
            )
            application_logger.info("File saved!")

            # Set appropriate permissions for ontology file again
            subprocess.call(['chmod', '0777', config.EXTENDED_IDS_ONTOLOGY_PATH])

        except Exception as e:
            application_logger.error(f"Exception caught while updating IDS ontology: {str(e)}")
            application_logger.error("Error in function (__merge_with_main_ontology)")
            application_logger.error(e, exc_info=True)

    def __save_graph_database(self, graph, basename, bool_import=False):
        """
        Save the graph database to a file and optionally import it to the remote database.

        Args:
            graph (Graph): The graph database to be saved.
            basename (str): The base name of the file to be saved.
            bool_import (bool, optional): Whether to import the file to the remote database. Defaults to False.
        """
        try:
            # Build the file path and filename
            file_path, filename = utils.build_filename(
                basename, self.base_resource_path)

            # Serialize the graph database to a file
            graph.serialize(
                destination=file_path, format=config.IDS_CORE_FORMAT_LOW_CHARACTERS, encoding='utf-8')

            # Merge the graph database with the main ontology
            self.__merge_with_main_ontology(graph)

            # Set file permissions
            p = subprocess.call(['chmod', '0777', file_path])

            # Log the file path
            application_logger.info(f"{file_path} file detected")

            if bool_import:
                # Generate the URL for importing the file to the remote database
                path_file = f"http://{config.HOST_NAME}:{str(os.environ.get('FLASK_APP_PORT'))}/api/get-rdf/" + filename

                # Log the URL
                application_logger.warning(path_file)

                # Import the file to the remote database
                self.database.remote_import_file(path_file, config.IDS_CORE_FORMAT)

        except Exception as e:
            # Log any exceptions that occur during the save process
            application_logger.error(
                f'Exception caught while saving file in the database: {str(e)}')
            application_logger.error(
                f'Error in function (__save_graph_database)')
            application_logger.error(e, exc_info=True)

    def save_and_return_rdf_database(self, file_json_name=config.CREATE_JSON_FILE):
        """
        Save the RDF database to a file and return the file path.

        Args:
            file_json_name (str): The name of the JSON file to be created.
                                Defaults to config.CREATE_JSON_FILE.

        Returns:
            str: The file path of the saved RDF database.
        """
        self.updating_ontology_mutex.acquire()
        try:
            file_path, root_name = utils.build_filename(
                file_json_name, self.base_resource_path, preffix="rdf")

            # Serialize the RDF graph to the file
            application_logger.info("Serializing file...")
            self.writing_graph.serialize(destination=file_path,format=config.PRETTY_FORMAT, encoding='utf-8')

            # Merge the serialized graph with the main ontology
            self.__merge_with_main_ontology(self.writing_graph)

            # Set the correct file permissions
            application_logger.info("Calling subprocess...")
            subprocess.call(['chmod', '0755', file_path])

            # Log the successful import
            application_logger.info(f"{str(file_path)} has been imported...")
        except Exception as e:
            # Log the exception if an error occurs
            application_logger.error(
                f'Exception caught, error while trying to create the JSON file: {str(e)}')
            application_logger.error('Error while trying to create the JSON file')
            application_logger.error(e, exc_info=True)

        self.updating_ontology_mutex.release()

        return file_path

    def __get_schema_type(self, content):
        """
        W3C XML Schema Definition Language (XSD) 1.1 Part 2: Datatypes
        Generated from: ../schemas/datatypes.xsd Date: 2021-09-05 20:37+10
        Args:
            content ([type]): [description]
        Returns:
            Returns the XSD code associated to the type of content
        """
        type_found = None
        if type(content) is str:
            type_found = XSD.string
        else:
            type_found = XSD.integer
        return type_found

    def find_metadata_in_graph(self, class_uri, metadata_map, property):
        """ Search on the database and on the current writing graph if there is
        an instance which has the same metadata in order to find the uri
        of this instance

        Args:
            class_uri ([URIRef]): Uri which identifies the class
            property (str): special property to find the instance in the database
            metadata_map (dict): Dictionary which contains the metadata of the class

        Returns:
            Returns a boolean True in case it could found the instance of the class and 
            returns the uri of the instance
        """
        found_node = False
        uri = None
        application_logger.info(
            f"Ready to find the metada in the graph... {str(config.PROPERTY_TITLE)}")
        for key, value_metadata in metadata_map.items():
            if ':' in key:
                key = key.split(':')[1]

            comparing_score = config.semantic_search.word_similarity_compare(
                key, config.PROPERTY_TITLE)

            if (key ==config.PROPERTY_TITLE) or (comparing_score > self.sim_threshold_main_property):
                application_logger.info(
                    f"Comparing properties: {str(key)} vs {str(config.PROPERTY_TITLE)}")
                if type(value_metadata) is dict:
                    for key, value in value_metadata:
                        application_logger.info(
                            f"Lets find the uri by using -> Value: {str(value)} Property: {str(property)} for the class: {str(class_uri)}")
                        uri = self.__auxiliary_find_metada_in_graph(
                            class_uri, property, value, config.semantic_search)
                        if uri:
                            break
                else:
                    application_logger.info(
                        f"Lets find the uri by using -> Value: {str(value_metadata)} Property: {str(property)} for the class: {str(class_uri)}")
                    uri = self.__auxiliary_find_metada_in_graph(
                        class_uri, property, value_metadata, config.semantic_search)
                if uri:
                    found_node = True
                    break
        return found_node, uri

    def __auxiliary_find_metada_in_graph(self, class_uri, property, value_metadata, measure):
        """
        Request the remote database and search on the current writing graph in order to find
        the uri of the instance of the class 
        """
        if not type(value_metadata) is list:
            value_metadata = [value_metadata]
        for value in value_metadata:
            # Try to find the instance requesting to the remote database
            application_logger.info(
                f"Search the value {str(value)} of property: {str(property)}")
            uri = self.database.request_current_node_in_database(
                class_uri, property, value)
            if uri:
                break
        if not uri:
            # Try to find the instance requesting to the current writing graph
            query_instances = self.writing_sparql.get_all_instances_class(
                class_uri)
            for value in value_metadata:
                uri = measure.find_uri_for_query(
                    query_instances, value, self.sim_threshold_property)
                if uri:
                    break
            # In case it could find the uri either on the database
            # or on the current graph return the uri of the instance
        return uri

    def reset_graph(self, reset_graph):
        """
        Resets the graph and initializes a new SparqlQuery object.

        Args:
            reset_graph: Boolean indicating whether to reset the graph.

        Raises:
            Exception: If an error occurs while resetting the graph.

        """
        try:
            self.writing_graph = reset_graph
            self.writing_sparql = SparqlQuery(self.writing_graph, self.ONTOLOGY_URI)

        except Exception as e:
            application_logger.error(
                f'Error while resetting Graph: {str(e)}')
            application_logger.error(e, exc_info=True)
