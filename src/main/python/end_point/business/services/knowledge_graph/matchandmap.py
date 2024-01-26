
from rdflib.namespace import DCTERMS
from transformers import AutoTokenizer, BertModel
import en_core_web_md  # spacy
import es_core_news_md

from end_point.business.services.knowledge_graph.complementary.match import Match
from end_point.business.services.knowledge_graph.complementary.map import Map
from end_point.business.services.ner.entityner import EntityNerPredictor
from end_point.logging_ita import application_logger
import end_point.config as config
from end_point.business import utils
import os
import re


class MatchAndMap():
    """
    Class which its only purpose is to execute the pipeline Match&Map
    """

    def __init__(self, wrapper):
        
        self.tokenizer_en, self.encoder_en = self.__initial_setup(os.environ.get("BERT_BASE_UNCASED_MODEL",'bert-base-uncased'))
        self.tokenizer_es, self.encoder_es = self.__initial_setup(os.environ.get("BERT_BASE_SPANISH_MODEL",'dccuchile/bert-base-spanish-wwm-uncased'))

        self.nlp_en = en_core_web_md.load()
        self.nlp_es = es_core_news_md.load()

        self.match = Match()
        self.already_done = False
        self.itaner = EntityNerPredictor()
        self.wrapper = wrapper
        self.dict_ontologies = self.wrapper.downloader.install_ontologies()

    def install_ontologies(self):
        """
        Install ontologies if not already done, and reset main ontology and map if already done.
        """
        if not self.already_done:
            # Import ontologies
            application_logger.info('Importing Ontologies...')
            self.main_ontology = self.wrapper.downloader.install_one_ontology(
                config.IDS_CORE_MAIN_ONTOLOGY[:-1], config.MAIN_ONTOLOGY_FILE,
                config.IDS_CORE_FORMAT, config.IDS_CORE_FORMAT_LOW_CHARACTERS, download_bool=False)
            
            self.map = Map(self.dict_ontologies, self.wrapper.downloader,
                        self.main_ontology)
            self.already_done = True
        else:
            # Reset main ontology and map
            self.main_ontology.reset_graph(
                self.wrapper.downloader.return_writing_graph())
            self.map = Map(self.dict_ontologies, self.wrapper.downloader,
                        self.main_ontology)

            application_logger.info('Ontologies have been imported')

    def __initial_setup(self, language_model):
        """
        Initialize tokenizer and encoder models for language processing.
        
        Args:
            language_model (str): Name of the language model to be used.
            
        Returns:
            tuple: A tuple containing the tokenizer and encoder models.
        """
        # Initialize tokenizer
        tokenizer = AutoTokenizer.from_pretrained(language_model)
        
        # Initialize encoder
        encoder = BertModel.from_pretrained(language_model)
        encoder.eval()
        
        # Return tokenizer and encoder
        return tokenizer, encoder

    def link_nodes_to_dataset(self, primary_node, description_content, ontology_access=None):
        """
        Links nodes to the dataset based on the primary node and description content.

        Args:
            primary_node (str): The primary node to link the nodes to.
            description_content (str): The description content to apply Match and Map.
            ontology_access (object, optional): The ontology access object. Defaults to None.
        """
        if primary_node and description_content:
            # Apply Match and Map to the description
            application_logger.info("Applying Match and Map to the description")
            list_nodes_to_link = self.apply_mama_pipe(description_content, primary_node)
            nodes_already_added = list()
            if list_nodes_to_link:
                # Add relations to the node recently created
                application_logger.warning("Adding relations to the node recently created")
                for remote_node in list_nodes_to_link:
                    if ontology_access:
                        if remote_node.get('id'):
                            if remote_node.get('id') not in nodes_already_added:
                                if remote_node.get('id') != primary_node:
                                    # Add new triplet to the ontology access
                                    ontology_access.add_new_triplet(primary_node, DCTERMS.description, utils.set_uriref_str(remote_node.get('id')))
                                    nodes_already_added.append(remote_node.get('id'))
                        else:
                            application_logger.warning("Something went wrong while looping through the nodes ID")

                # Update index
                application_logger.info("Updating index...")
                self.wrapper.search_index.update_elastic_search_index_consulting(list_nodes_to_link)
            else:
                application_logger.error("No data available to update...")
        else:
            application_logger.info("No class nor description content")

    def apply_mama_pipe(self, input_plain_text, remote_node_uri=None):
        """ Apply the match and map pipeline to the text passed as parameters

        Args:
            input_plain_text (str): Text to be proccessed.
        Returns:
            List<{
                id: Uri node,
                content: dictionary
            }>
        """
        self.install_ontologies()

        application_logger.info("Let's the mapping begin:")

        populating_content_for_elasticsearch = list()

        lines = None
        lines = re.split("\.|\n", input_plain_text)
        for line in lines:
            sentence = line.strip()
            valid_triplets = list()
            if len(sentence) > 1:
                application_logger.info("Detecting language....")
                application_logger.info(sentence)
                language = utils.detect_metadata_language(sentence)
                application_logger.info(f"Language detected: {str(language)}")
                if language == 'es':
                    nlp = self.nlp_es
                    tokenizer = self.tokenizer_es
                    encoder = self.encoder_es
                    stopwords = config.invalid_relations_set_es
                elif language == 'en':
                    nlp = self.nlp_en
                    tokenizer = self.tokenizer_en
                    encoder = self.encoder_en
                    stopwords = config.invalid_relations_set_en
                else:
                    application_logger.warning(
                        f"It should be either Spanish or English, It is {str(language)}")
                    break

                self.match.set_match_stopwords(stopwords)
                application_logger.info("Starting to process sentences")
                list_prediction_entity = self.itaner.ner_predict(sentence)
                application_logger.info("These are the predictions")
                application_logger.info(list_prediction_entity)
                for entity, prediction in list_prediction_entity:
                    config.db_cache.add_entity_prediction(entity, prediction)

                for sent in nlp(sentence).sents:
                    # Match
                    text_to_map = str(sent.text).strip()
                    for triplets in self.match.parse_sentence(text_to_map, tokenizer, encoder, nlp):
                        valid_triplets.append(triplets)
                try:
                    application_logger.info("Starting to process triplets")
                    for triplet in valid_triplets:
                        if language == 'es':
                            relation = triplet['r']
                            relation = relation[0]
                            relation = config.translator.translate(relation)
                            triplet['r'] = [relation]
                        info_triple =f""" 
                        ------------------INFO TRIPLET------------------------
                        {str(triplet)}
                        ------------------------------------------------------
                        """
                        application_logger.info(info_triple)
                        populating_triplet = self.map.brute_force_mapping(
                            triplet, input_plain_text, self.wrapper.search_index, remote_node_uri, language)
                        if populating_triplet:
                            populating_content_for_elasticsearch = populating_content_for_elasticsearch + \
                                populating_triplet
                except Exception as e:
                    application_logger.error(f"Exception caught while looping triplets: {str(e)}")
                    application_logger.error(e, exc_info=True)

        application_logger.info("Saving data...")
        self.map.main_ontology.save_graph_in_rdf_format()
        application_logger.info("Saving data: Done")
        self.wrapper.search_index.update_elastic_search_index_consulting(
            populating_content_for_elasticsearch)
        application_logger.info("Mapping done!")

        return populating_content_for_elasticsearch
