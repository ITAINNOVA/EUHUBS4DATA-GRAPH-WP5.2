
from end_point.business import utils
from rdflib import URIRef, Literal
from end_point.logging_ita import application_logger
from end_point.config import db_cache
import end_point.config as config
import re
from rdflib.namespace import RDF, RDFS, OWL, XSD, DCTERMS

class Map:
    """
    Class used for mapping the triplets which have been processed by the Match class.
    This class used instances of Ontology Access for mapping the triplets to the
    ontology vocabulary which theses instances contains.
    """

    def __init__(self, ontology_access, onto_downloader, main_ontology_access) -> None:
        self.measure = config.semantic_search
        self.sim_threshold_class = 0.75
        self.sim_threshold_content = 0.95
        self.dict_ontology_access = ontology_access
        self.main_ontology = main_ontology_access
        self.downloader = onto_downloader

    def mix_mapping(self, triplet, search_index_class, language='en'):
        """Map a triplet composed by {h: head,r:relation,t:tail}
            into the ontology using ontology's vocabulary
        Args:
            triplet (dict): Triplet composed by: {h: head,r:relation,t:tail}
        """
        head = triplet.get('h').strip()
        head_ontology_access = None
        tail_ontology_access = None
        relation = triplet.get('r')
        relation = relation[0].strip()
        head_instance_uri = None
        tail_instance_uri = None
        object_property = None
        datatype_property = None
        high_similarity = 0
        # Search if there is a class available forf the head and
        # if it could find any instance of this class
        application_logger.info(
            f"Search the most suitable class for: {str(head)}")

        # Now the head has been created, it is necessary to find the tail
        try:
            # Search for ontology, class and instance
            head_prediction_class, head_instance_uri, head_ontology_access = self.search_instance_and_class_for_query(
                head, search_index_class, language)

            if head_prediction_class is not None and head_ontology_access is not None:

                # Find what are the head and the tail in the NER
                tail = triplet.get('t').strip()
                # Do the same with the tail
                # Search for the class and the instance of the tail

                try:
                    tail_prediction_class, tail_instance_uri, tail_ontology_access = self.search_instance_and_class_for_query(
                        tail, search_index_class, language)
                    # Once both classes have been found it is time to deal with the relation
                    # The relation could be an obecty property or a data property
                    datatype_property_list, object_property_list = head_ontology_access.get_all_properties_of_class_witch_cache(
                        head_prediction_class)
                    # In case there is a instance of a class which is the tail

                    if tail_instance_uri and tail_prediction_class:
                        # Check if one of them belongs to the main ontology
                        if self.main_ontology.ONTOLOGY_URI == head_ontology_access.ONTOLOGY_URI or self.main_ontology.ONTOLOGY_URI == tail_ontology_access.ONTOLOGY_URI:
                            application_logger.info(
                                "One of them belongs to the main ontology...")
                            dict_ontology = db_cache.get_map_metadata(relation)
                            #  The relation must be an object property
                            if dict_ontology is not None:
                                application_logger.info("Mapped properties!")
                                object_property = dict_ontology.get('property')
                                high_similarity = dict_ontology.get(
                                    'similarity')
                            else:
                                try:
                                    application_logger.info(
                                        "SEMANTIC RULES: Seeking for the correct object property")
                                    object_property, object_range, high_similarity = head_ontology_access.search_sim_key_object_property_list(
                                        relation, object_property_list, self.sim_threshold_class)
                                    db_cache.add_new_map_metadata(
                                        relation, {'property': object_property, 'similarity': high_similarity})

                                    application_logger.info(
                                        f"Posible option -> {str(object_property)} -> {str(high_similarity)}")
                                except Exception as e:
                                    application_logger.error(
                                        "Error while seeking property...")
                                    application_logger.error(str(e))
                                    application_logger.error(e, exc_info=True)

                            if object_property is not None:
                                application_logger.info(
                                    "It is supposed to be an Object Property")
                                self.main_ontology.add_new_triplet(
                                    URIRef(head_instance_uri), object_property, URIRef(tail_instance_uri))
                            else:
                                application_logger.warning(
                                    f"There is not such a relation: ({str(relation)}) between {str(head)} and {str(tail)}")
                                populating_ontology = None
                                if self.main_ontology.ONTOLOGY_URI == head_ontology_access.ONTOLOGY_URI:
                                    populating_ontology = head_ontology_access
                                else:
                                    populating_ontology = tail_ontology_access

                                if populating_ontology is not None:
                                    object_property = populating_ontology.add_new_objecttype_to_ontology(
                                        relation, head_prediction_class, tail_prediction_class)
                                    application_logger.info(
                                        "Try to add this new relation to the ontology...")
                                    if object_property:
                                        populating_ontology.add_new_triplet(
                                            utils.set_uriref_str(head_instance_uri), utils.set_uriref_str(object_property), URIRef(tail_instance_uri))
                                    else:
                                        application_logger.error(
                                            f"It was not possible to add {str(relation)} as a new relation")
                                else:
                                    application_logger.error(
                                        f"Main ontology is not being populating...")
                        else:
                            application_logger.error(
                                f"Main ontology is not being populating...")
                    else:
                        # When the tail does not exists, the relation must be a datatype property
                        if self.main_ontology.ONTOLOGY_URI == head_ontology_access.ONTOLOGY_URI:
                            application_logger.info(
                                "The tail no exists so it has to be data type property")
                            # Check if the head is the main ontology
                            dict_ontology = db_cache.get_map_metadata(relation)
                            if dict_ontology:
                                datatype_property = dict_ontology.get(
                                    'property')
                                high_similarity = dict_ontology.get(
                                    'similarity')
                            else:
                                try:
                                    application_logger.info(
                                        "SEMANTIC RULES: Seeking for the correct datatype property")
                                    datatype_property, high_similarity = head_ontology_access.search_sim_key_datatype_property_list(
                                        relation, datatype_property_list, self.sim_threshold_class)
                                    db_cache.add_new_map_metadata(
                                        relation, {'property': datatype_property, 'similarity': high_similarity})
                                    application_logger.info(
                                        f"Posible option -> {str(datatype_property)} -> {str(high_similarity)}")
                                except Exception as e:
                                    application_logger.error(
                                        "Error while seeking property...")
                                    application_logger.error(e, exc_info=True)

                            if datatype_property is not None:
                                head_ontology_access.add_new_triplet(
                                    utils.set_uriref_str(head_instance_uri), utils.set_uriref_str(datatype_property), Literal(tail))
                            else:
                                application_logger.info(
                                    f"Try to add this new property ({str(relation)}) to the ontology...")

                                datatype_property = head_ontology_access.add_new_datatype_to_ontology(
                                    relation, head_prediction_class, tail)

                                if datatype_property is not None:
                                    application_logger.info(
                                        f"{str(datatype_property)} is about to be created")

                                    head_ontology_access.add_new_triplet(
                                        utils.set_uriref_str(head_instance_uri), utils.set_uriref_str(datatype_property), Literal(tail))
                                    application_logger.info(
                                        f"Saving the triplets...")
                                else:
                                    application_logger.error(
                                        f"It was not possible to add {str(relation)} as a new property")
                        else:
                            application_logger.error(
                                f"Main ontology is not being populating...")
                except Exception as e:
                    application_logger.error(
                        f'Exception caught while searching an instance for the tail class: {str(e)}')
                    application_logger.error(e, exc_info=True)

            else:
                application_logger.error(f"No class found for: {str(head)}")
                # Write the current graph on a file and import this file to the database
        except Exception as e:
            application_logger.error(
                f'Exception caught while searching an instance for the head class: {str(e)}')
            application_logger.error(e, exc_info=True)
        return head_instance_uri, tail_instance_uri

    def brute_force_mapping(self, triplet, sentence_content, search_index_class, remote_node_uri=None, language='en'):
        """
        This function performs brute force mapping of a triplet, creating content to feed the index.
        
        Args:
            triplet (dict): The triplet to be mapped.
            sentence_content (str): The sentence content for populating the index.
            search_index_class (class): The search index class.
            remote_node_uri (str, optional): The remote node URI. Defaults to None.
            language (str, optional): The language of the content. Defaults to 'en'.
        
        Returns:
            list: The populated content.
        """
        populate_content = list()
        head_instance_uri = None
        tail_instance_uri = None
        
        # Clean triplet values
        triplet['h'] = re.sub(r",|-|_", " ", str(triplet.get('h'))).strip()
        triplet['t'] = re.sub(r",|-|_", " ", str(triplet.get('t'))).strip()
        triplet['r'][0] = re.sub(r",|-|_", "", str(triplet['r'][0])).strip()
        
        try:
            # Check if triplet values are alphanumeric and meet length criteria
            if re.match("^\w+", str(triplet.get('h'))) and re.match("^\w+", str(triplet.get('t'))) and re.match("^\w+", triplet.get('r')[0]):
                if len(str(triplet.get('h'))) > 3 and len(str(triplet.get('t'))) > 3 and len(str(triplet.get('r')[0])) > 1 and not triplet.get('r')[0][0].isupper():
                    # Perform mixture mapping and get head and tail instance URIs
                    head_instance_uri, tail_instance_uri = self.mix_mapping(triplet, search_index_class, language)
                    application_logger.info("Creating content to feed the index...")
                    
                    # Detect language of sentence content and translate if necessary
                    language = utils.detect_metadata_language(sentence_content)
                    if language != 'en':
                        sentence_content = config.translator.translate(sentence_content)
                    
                    # Create content for populating the index
                    populate_content = self.create_content_for_populating(remote_node_uri, sentence_content, populate_content)
                    populate_content = self.create_content_for_populating(head_instance_uri, str(triplet.get('h')), populate_content)
                    populate_content = self.create_content_for_populating(tail_instance_uri, str(triplet.get('t')), populate_content)
                    application_logger.info("Content for the dataset prepared!")
                else:
                    application_logger.warning("I do not like the relation")
            else:
                application_logger.warning("I do not like the triplet")
        
        except Exception as e:
            application_logger.error(f'Exception caught (brute_force_mapping): {str(e)}')
        
        return populate_content

    def create_content_for_populating(self, uri, content, populate_list):
        """
        Create content for populating the given populate_list with a new dictionary containing uri and content.

        Args:
            uri: The uri value for the new dictionary.
            content: The content value for the new dictionary.
            populate_list: The list to populate with the new dictionary.

        Returns:
            The updated populate_list.
        """
        if uri is not None:
            new_dict_populate = {
                'id': uri,
                'content': content
            }
            populate_list.append(new_dict_populate)

        return populate_list

    def __search_similar_for_candidate(self, candidate, ontology_access):
        """Auxiliary function used to search the most similar class to a given query.

        Args:
            candidate (URIRef): Query of the class
            onotology_access(OntologyAccess):

        Returns:
            (URIRef, Integer): Returns the best class candidate to the given query and the
            highest score found
        """
        best_candidate_predict = None
        try:

            class_candidate, score_class = ontology_access.get_most_similar_class_uriref(
                candidate)

            if class_candidate and score_class > self.sim_threshold_class:
                best_candidate_predict = class_candidate

        except Exception as e:
            application_logger.error(
                f'Exception caught (__search_similar_for_candidate): {str(e)}')
            application_logger.error(
                f"Error while searching for a smiliar class to: {str(candidate)}")
            application_logger.error(e, exc_info=True)

        return best_candidate_predict

    def __save_entity_prediction(self, query):
        """
        Save the entity prediction for a given query.

        Args:
            query (str): The query to save the prediction for.

        Returns:
            str: The entity prediction for the query.
        """

        ner_prediction = None
        similary_query = None

        # Check if there is a prediction for this query
        application_logger.info(f"Checking if there is a prediction for this query: {str(query)}")
        ner_prediction = db_cache.get_entity_prediction(query)

        if not ner_prediction:
            # Transform the query into a clean format
            clean_query = utils.transform_class_name(query)
            highest_score = 0
            content_list = db_cache.get_entity_prediction_dict()

            # Apply similarity metrics
            application_logger.info(f"Applying similarity metrics...")
            list_possible_options = list()

            try:
                # Find something close to the query
                application_logger.info(f"No prediction, about to find something close...")
                for content, label in content_list.items():
                    try:
                        clean_content = utils.transform_class_name(str(content))

                        # Compare the similarity between the clean query and clean content
                        score = config.semantic_search.word_similarity_compare(clean_query, clean_content)

                        # Add the prediction if it meets the similarity threshold or contains the query
                        if (score > self.sim_threshold_class) or (clean_query in clean_content) or (clean_content in clean_query):
                            dict_prediction_class = {
                                'label': label,
                                'content': content
                            }
                            list_possible_options.append(dict_prediction_class)
                    except Exception as e:
                        application_logger.error(f"Error finding similarities with {str(content)}: Error: {str(e)}")
                        application_logger.error(e, exc_info=True)

                # Apply semantics rules
                application_logger.info(f"Applying semantics rules...")
                for prediction_candidate in list_possible_options:
                    try:
                        content = prediction_candidate.get('content')
                        label = prediction_candidate.get('label')
                        clean_content = utils.transform_class_name(str(content))

                        # Calculate the semantic score between the clean query and clean content
                        semantic_score = config.syns_maker.semantic_english_score(clean_query, clean_content)

                        # Update the prediction if the semantic score is higher than the previous one
                        if semantic_score > highest_score and semantic_score > 0.2:
                            highest_score = semantic_score
                            ner_prediction = label
                            similary_query = content
                    except Exception as e:
                        application_logger.error(str(e))
                        application_logger.error(e, exc_info=True)

                if ner_prediction:
                    # Save the new prediction
                    application_logger.info(f"Saving new prediction: {str(query)} <-> {str(ner_prediction)}")
                    db_cache.add_entity_prediction(query, ner_prediction)

                    if similary_query:
                        # Link the new query to the similar query
                        application_logger.info(f"Prediction -> {str(query)} -> {str(similary_query)} -> {str(ner_prediction)}")
                        uri_triplet = db_cache.get_uri_of_title(str(similary_query))

                        if uri_triplet:
                            # Link the new query to the URI of the similar query
                            application_logger.info(f"Linking new query {str(query)} to -> {str(similary_query)}")
                            self.main_ontology.add_alternative_title_triplet(uri_triplet, query)
                            db_cache.add_new_title_uri(query, uri_triplet)
                        else:
                            application_logger.warning(f"No previous URI, it has to find one")
            except Exception as e:
                application_logger.error(f"Error while saving NER prediction Error:{str(e)}")
                application_logger.error(e, exc_info=True)
        else:
            application_logger.info(f"Prediction: {str(ner_prediction)}")

        return ner_prediction

    def __auxiliary_save_prediction_and_get_class(self, query):
        """
        This function saves the entity prediction for a given query and returns the corresponding class.

        Args:
            query (str): The input query.

        Returns:
            str or None: The predicted class for the query, or None if no prediction is available.
        """

        prediction_class = None
        try:
            # Save the entity prediction
            ner_prediction = self.__save_entity_prediction(query)
            if ner_prediction:
                # Check if there is an available class for the query
                # The first step involves searching for the class in the main ontology
                prediction_class = self.__get_cache_content_class(ner_prediction, self.main_ontology)
            else:
                application_logger.warning(f"WARNING, no detected NER prediction {str(ner_prediction)} -> {str(query)}.")
        except Exception as e:
            application_logger.error(f"Error while predicting NER for {str(query)} Error: {str(e)}")
            application_logger.error(e, exc_info=True)
        
        return prediction_class

    def map_just_one_concept_to_node(self, primary_node, query, search_index_class, special_relation, main_ontology, language='en'):
        """
        Maps just one concept to a node in the ontology.

        Args:
            primary_node (str): The URI of the primary node.
            query (str): The query to search for.
            search_index_class (SearchIndexClass): The search index class.
            special_relation (str): The special relation to add between the primary node and the concept node.
            main_ontology (MainOntology): The main ontology.
            language (str, optional): The language for the query. Defaults to 'en'.

        Returns:
            str: The URI of the concept node.
        """
        head_instance_uri = None
        populate_list = list()
        try:
            # Log the query
            application_logger.warning(query)

            # Search for the instance and class for the query
            head_prediction_class, head_instance_uri, populating_ontology = self.search_instance_and_class_for_query(
                query, search_index_class, language)

            if head_instance_uri:
                # Add a new triplet between the primary node and the concept node
                main_ontology.add_new_triplet(
                    URIRef(primary_node), URIRef(special_relation), URIRef(head_instance_uri))

                # Create content for populating the concept node
                populate_list = self.create_content_for_populating(
                    head_instance_uri, query, populate_list)

                # Update the search index with the populated content
                search_index_class.update_elastic_search_index_consulting(
                    populate_list)
        except Exception as e:
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

        return head_instance_uri

    def semantic_analyse_class_results(self, list_classes, query, language):
        """
        Analyzes the semantic score of each class in the given list and returns the class with the highest score.

        Args:
            list_classes (list): List of dictionaries containing class information.
            query (str): The query string to compare against the class sentences.
            language (str): The language of the sentences ('es' for Spanish, 'en' for English).

        Returns:
            tuple: A tuple containing the URI of the best class and its corresponding semantic score.
        """
        best_score = 0
        query = utils.transform_class_name(query).strip()
        best_class = None

        for query_sentence_class in list_classes:
            sentence = utils.delete_ontology_preffix(
                query_sentence_class.get('sentence'))
            sentence = utils.transform_class_name(sentence).strip()
            try:
                if language == 'es':
                    semantic_score = config.syns_maker.semantic_spanish_score(
                        query, sentence)
                else:
                    semantic_score = config.syns_maker.semantic_english_score(
                        query, sentence)
                
                if semantic_score > best_score:
                    best_score = semantic_score
                    best_class = utils.set_uriref_str(
                        query_sentence_class.get('uri'))

            except Exception as e:
                error_message = f"""
                Error while analyzing semantic score of class.
                query: {str(query)}
                language: {str(language)}
                Error: {str(e)}
                """
                application_logger.error(error_message)
                application_logger.error(e, exc_info=True)

        return best_class, best_score

    def search_instance_and_class_for_query(self, query, search_index_class, language='en'):
        """ Search and tries to find the class and instances of this class
        according to a query.

        Args:
            query ([str]): [description]

        Returns:
            [(URIRef,URIRef)]: Returns the URI of the class and the URI of the corresponded instance
            to the query

        """
        class_instance_uri = None
        ontology_access = None
        prediction_class = None
        list_prediction_class = list()
        try:
            if search_index_class is not None:
                cache_prediction_class = db_cache.get_class_of_prediction(
                    query)
                if not cache_prediction_class:
                    application_logger.info(
                        f"Let's find this query in the index {str(query)}")

                    # search_in_index_es_dbpedia
                    if language == 'es':
                        list_prediction_class = search_index_class.search_in_index_es_dbpedia(
                            query)
                    else:
                        list_prediction_class = search_index_class.search_in_index_dbpedia(
                            query)
                    #####################################################################################################
                    # USE SEMANTIC SEARCH
                    #
                    #####################################################################################################
                    prediction_class, prediction_score = self.semantic_analyse_class_results(
                        list_prediction_class, query, language)
                    #####################################################################################################
                    #
                    #####################################################################################################
                    application_logger.info(
                        f"Option in dbpedia index: {str(prediction_class)} --> {str(prediction_score)}")

                    if prediction_class and prediction_score > 0.4:
                        prediction_class = utils.set_uriref_str(
                            prediction_class)
                        db_cache.add_new_prediction_class(
                            query, prediction_class)
                    else:
                        application_logger.info(
                            f"Let's find it on the ontologies...")
                        prediction_class = self. __auxiliary_save_prediction_and_get_class(
                            query)
                else:
                    prediction_class = cache_prediction_class
            else:
                application_logger.warning("No DBpedia...")
                prediction_class = self. __auxiliary_save_prediction_and_get_class(
                    query)
            # Search the class in the main ontology
            # In case it has been found
            if prediction_class is not None:
                application_logger.info(
                    "The ontology found it is the main ontology...")
                # Create an instance for the class in the main ontology
                application_logger.info(
                    f"{str(query)} <-> {str(prediction_class)}")
                class_instance_uri = self.save_cache_content_uri(
                    query, prediction_class, self.main_ontology)
                ontology_access = self.main_ontology
                application_logger.info(
                    f"URI for the class {str(prediction_class)} : {str(class_instance_uri)}")
            else:
                # The class it is no in the main ontology
                # Check it in the secondary ontologies
                ner_prediction = self.__save_entity_prediction(query)
                ontology_ner_prediction = self.dict_ontology_access.get(
                    ner_prediction)
                application_logger.info(
                    f"NER PREDICTION -> {str(ner_prediction)}")
                if ontology_ner_prediction is not None:
                    application_logger.info(
                        "An ontology has been found...")
                    # Search for the class in the ontology
                    application_logger.info(
                        f"Search for the class in the NER ontology")
                    prediction_class = self.__get_cache_content_class(
                        ner_prediction, ontology_ner_prediction)
                    if prediction_class is not None:
                        # Create and search an instance for the prediction class
                        class_instance_uri = self.save_cache_content_uri(query, prediction_class, ontology_ner_prediction)
                        application_logger.info(
                            f"Instance created for: {str(prediction_class)} -> {str(class_instance_uri)}")
                        ontology_access = ontology_ner_prediction
                    else:
                        application_logger.warning(
                            f"No class suitable for the NER prediction: {str(prediction_class)}")
                else:
                    application_logger.warning(
                        f"No Ontology for the NER prediction: {str(prediction_class)}")

        except Exception as e:
            application_logger.error(
                f'Exception caught (search_instance_and_class_for_query(): {str(e)}')
            application_logger.error(e, exc_info=True)
            application_logger.error(
                f"Error while searching for class to:{str(query)}")

        return prediction_class, class_instance_uri, ontology_access

    def save_cache_content_uri(self, query, prediction_class, ontology_access):
        """
        Save the cache content URI for a given query.

        Args:
            query (str): The query to save the cache for.
            prediction_class (str): The prediction class.
            ontology_access (str): The ontology access.
        Returns:
            str: The class instance URI.
        """
        # Get the URI of the cache title
        cache_title_uri = db_cache.get_uri_of_title(query)

        class_instance_uri = None

        if cache_title_uri:
            # If the cache title URI exists, set the class instance URI and log the cache
            class_instance_uri = cache_title_uri
            application_logger.info(
                f"Cache {str(query)} --> uri: {str(class_instance_uri)}"
            )
        else:
            # If the cache title URI does not exist, search for the instance class and set the class instance URI
            application_logger.info(f"No Cache uri for {str(query)}")
            class_instance_uri = self.search_instance_class(
                query, prediction_class, ontology_access
            )

        if not cache_title_uri and class_instance_uri:
            # If the cache title URI does not exist and the class instance URI exists, add a new title URI to the cache
            db_cache.add_new_title_uri(query, class_instance_uri)

        return class_instance_uri

    def __get_cache_content_class(self, ner_prediction, acces_ontology):
        """
        Get the cache content class for a given NER prediction and access to the ontology.

        Args:
            ner_prediction (str): The NER prediction.
            acces_ontology (str): The access to the ontology.

        Returns:
            str: The cache content class.
        """
        # Get the class of the prediction from the cache
        cache_prediction_class = db_cache.get_class_of_prediction(ner_prediction)

        prediction_class = None
        if cache_prediction_class:
            # Log the cache content class if it exists
            application_logger.info(
                f"Cache {str(ner_prediction)} -> class: {str(cache_prediction_class)}")
            prediction_class = cache_prediction_class
        else:
            # Log that there is no cache class for the prediction
            application_logger.info(
                f"No Cache class for {str(ner_prediction)}")

            # Search for a similar candidate for the prediction
            prediction_class = self.__search_similar_for_candidate(
                ner_prediction, acces_ontology)
        if not cache_prediction_class and prediction_class:
            # Cache the prediction class if it is not in the cache and a candidate is found
            application_logger.info(
                f"Caching prediction -> {str(prediction_class)}")
            db_cache.add_new_prediction_class(ner_prediction, prediction_class)
            application_logger.info("Caching prediction... DONE")

        return prediction_class

    def search_instance_class(self, query, query_class, ontology_access):
        """
        Search for an instance of a given class based on a query.
        
        Args:
            query (str): The query string.
            query_class (str): The class to search for instances.
            ontology_access (OntologyAccess): An instance of the OntologyAccess class.
        Returns:
            str: The URI of the new instance.
        """
        new_instance = None
        try:
            # Get all instances of the class
            application_logger.info(f"Requesting all instances for the class: {str(query_class)}")
            
            # Request instances from the database
            query_database = ontology_access.database.request_all_instances_class(query_class)
            
            # Search instance on the writing graph
            query_graph = ontology_access.writing_sparql.get_all_instances_class(query_class)
            
            # Combine instances from the database and graph
            query_instances = query_database + query_graph
            
            if query_instances:
                application_logger.info(f"A list of queries found for this class")
                
                # Find the URI for the query
                new_instance = self.measure.find_uri_for_query(query_instances, query, self.sim_threshold_content)
                
                # Create new instances if not found
                new_instance = self.__create_new_instances(new_instance, query, query_class, ontology_access)
            else:
                application_logger.info(f"No queries found, it has to create one")
                
                # Create a new instance for the class
                new_instance = self.__create_new_instances(new_instance, query, query_class, ontology_access)                
                application_logger.info(f"URI CREATED {str(new_instance)}")

        except Exception as e:
            error_message = f"""
            Exception caught, error in (search_instance_class): {str(e)}
            Class: {str(query_class)} Query: {str(query)}
            """
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)
            
        return new_instance

    def __create_new_instances(self, new_instance, query, query_class, ontology_access):
        """
        Create new instances if no previous instance is found.

        Args:
            new_instance (str): The new instance.
            query (str): The query.
            query_class (str): The query class.
            ontology_access (OntologyAccess): The ontology access object.
        Returns:
            str: The new instance.
        """
        # Check if a new instance needs to be created
        if not new_instance:
            # If no previous instance is found, add a new one
            application_logger.warning("No previous instance found, adding new one...")
            new_instance = ontology_access.add_new_datatype_triplet(query, query_class)
            if new_instance:
                application_logger.info(f"Instance created for: {query_class} -> {new_instance}")
            else:
                application_logger.warning(f"No instance created, ERROR: {query_class}")
        else:
            # A previous instance is found
            application_logger.info(f"Instance found for: {query_class} -> {new_instance}")

        return new_instance
