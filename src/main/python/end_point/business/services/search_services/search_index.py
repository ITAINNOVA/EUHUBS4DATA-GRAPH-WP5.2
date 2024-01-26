
from end_point.logging_ita import application_logger
import end_point.config as config
from elasticsearch import Elasticsearch
from end_point.business import utils
import threading
import pandas as pd


class SemanticSearchIndex():
    """
    This class is used to access to the instance of ElasticSearch.
    UPDATE AND SEARCH FOR DOCS in the ElasticSearch index.

        Tutorial: https://github.com/UKPLab/sentence-transformers/blob/master/examples/applications/semantic-search/semantic_search_quora_elasticsearch.py
        Install ElasticSearch :(https://www.elastic.co/de/elasticsearch/) up and running.
        Further, you need the Python ElasticSearch Client installed: https://elasticsearch-py.readthedocs.io/en/master/
        Models for embedding:
            'sentence-transformers/paraphrase-xlm-r-multilingual-v1'

        In case ElasticSearch fails: https://sleeplessbeastie.eu/2020/02/29/how-to-prevent-systemd-service-start-operation-from-timing-out/

        Auxiliary tutorial: https://dzlab.github.io/nlp/2021/08/09/elasticsearch_bert/
    """

    def __init__(self):
        self.consulting_index_name = 'consulting_index'
        self.dbpedia_index_name = 'dbpedia_index'
        self.dataset_text = "dataset"
        self.mutex = threading.Lock()
        self.elsearch = Elasticsearch(
            [config.ELASTIC_NODE],
            # sniff before doing anything
            sniff_on_start=True,
            # refresh nodes after a node fails to respond
            sniff_on_connection_fail=True,
            # and also every 60 seconds
            sniffer_timeout=60,
            timeout=45,
            max_retries=10,
            retry_on_timeout=True,
            # Solution propused on:
            # https://stackoverflow.com/questions/39640200/elasticsearch-python-client-work-with-many-nodes-how-to-work-with-sniffer
            sniff_timeout=30,
            http_auth=(config.ELASTIC_USER, config.ELASTIC_PASSWORD),
            propagate=True)
        self.create_elastic_search_index_all()


########################################################
#
# GENERAL INDEX METHODS
#
# ###################################################


    def create_elastic_search_index(self, index_name=None, doc_index={}):
        """
        Creates the ElasticSearch index in case it does not exists
        """
        bool_new_index = False
        try:
            if not self.elsearch.indices.exists(index=index_name):
                es_index = doc_index
                """
                Solution for the error: 
                [TOO_MANY_REQUESTS/12/disk usage exceeded flood-stage watermark, index has read-only-allow-delete block];
                StackOverflow:
                https://stackoverflow.com/questions/50609417/elasticsearch-error-cluster-block-exception-forbidden-12-index-read-only-all
                Documentation:
                https://www.elastic.co/guide/en/elasticsearch/reference/6.2/disk-allocator.html
                """
                self.elsearch.indices.create(
                    index=index_name, body=es_index, ignore=[400])
                application_logger.warning(
                    f"The index -> {str(index_name)} created...")
                bool_new_index = True
            else:
                application_logger.warning("The index already exists...")
        except Exception as e:
            application_logger.error(
                f"During index an exception occured. -> {str(e)}")
            application_logger.error(e, exc_info=True)
        return bool_new_index

    def update_elastic_search_index(self, datasets_dict, index_name):
        """
        Updates the index with new datasets.
        """
        self.mutex.acquire()
        try:
            application_logger.info(
                f"Updating index -> {str(len(datasets_dict))}")
            for dataset in datasets_dict:
                dataset_content = dataset.get('content')
                node_id = dataset.get('id')
                if dataset_content and node_id:
                    try:
                        embbeded_dataset = config.semantic_search.get_word_embeddings(
                            dataset_content).tolist()
                        doc = {
                            "dataset": dataset_content,
                            "dataset_vector": embbeded_dataset
                        }
                        res = self.elsearch.index(
                            index=index_name, id=node_id, body=doc)
                    except Exception as e:
                        application_logger.error(
                            f"Exception caught -> {str(e)}")
                        application_logger.error(
                            f"Error while indexing -> {str(dataset_content)}   <-> {str(node_id)}")
                        application_logger.error(e, exc_info=True)

        except Exception as e:
            error_message = f"""
            Error while updating index: {str(index_name)}
            Error: {str(e)}
            Dataset: {str(datasets_dict)}
            """
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)
        self.mutex.release()

    def search_in_index(self, query_search, index_name=None, body_query={}):
        """
        Searches in the index the document whose embeddings have the 
        highest cosine similarity
        Returns a list of URIs
        """
        uri_list = list()
        already_found_uri_list = list()
        try:
            sem_search = self.elsearch.search(
                index=index_name, body=body_query)
            if sem_search:
                hits_result = sem_search.get('hits')
                if hits_result:
                    hits_result = hits_result.get('hits')
                    if hits_result:
                        for hits in hits_result:
                            uri_result = hits.get('_id')
                            uri_score = hits.get('_score')
                            uri_content = hits.get('_source')

                            if uri_result and uri_score and uri_content:
                                if not uri_result in already_found_uri_list:
                                    uri_list.append({
                                        'uri': uri_result,
                                        'score': uri_score,
                                        self.dataset_text: uri_content.get(
                                            self.dataset_text)
                                    })
                                    already_found_uri_list.append(uri_result)
                    else:
                        application_logger.warning(
                            f"No hits for {query_search}")
                else:
                    application_logger.warning(f"No hits for {query_search}")
            else:
                application_logger.warning(f"No results for {query_search}")

        except Exception as e:
            error_message = f"""
            Error while searching file in index: {str(index_name)}
            Error: {str(e)}
            Query: {str(query_search)}
            Body: {str(body_query)}
            """
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)

        return uri_list

    def parse_dict_and_update(self, json_graph, index_name=None):
        """
        Parses a json dictionary and updates the ElasticSearch index
        """
        content_list = list()
        node_title = None
        try:
            original_json = json_graph.get("results")
            if original_json:
                original_json = original_json[0]
                original_json = original_json.get("data")
                if original_json:
                    for graph in original_json:
                        graph = graph.get("graph")
                        nodes = graph.get("nodes")
                        if nodes:
                            for node in nodes:
                                if node.get('properties'):
                                    node_properties = node.get('properties')
                                    node_id = node_properties.get('uri')
                                    #    Check tooltip and events http://cytoscape.github.io/cytoscape.js/#core/events
                                    #   https://stackoverflow.com/questions/20993149/how-to-add-tooltip-on-mouseover-event-on-nodes-in-graph-with-cytoscape-js
                                    # The json properties is transformed into html content in order to show it in the tooltips
                                    node_description = node_properties.get(
                                        'https://w3id.org/idsa/core/description')
                                    if not node_description:
                                        node_description = node_properties.get(
                                            'http://purl.org/dc/terms/description')

                                    node_title = node_properties.get(
                                        utils.get_uriref_str(config.NODE_PROPERTY_NAME))

                                    if node_description:
                                        if type(node_description) is list and len(node_description) > 0:
                                            node_description = node_description[0]

                                    if node_title:
                                        if type(node_title) is list and len(node_title) > 0:
                                            node_title = node_title[0]

                                    if node_title and node_id:
                                        new_tmp_content = str(
                                            node_title).strip()
                                        if node_description:
                                            new_tmp_content = new_tmp_content + \
                                                ". " + \
                                                str(node_description).strip()

                                        content_list.append({
                                            'id': node_id,
                                            'content': new_tmp_content
                                        })

                                    else:
                                        if node_description and node_id:
                                            content_list.append({
                                                'id': node_id,
                                                'content': str(node_description).strip()
                                            })
                                        else:
                                            application_logger.error(
                                                f"Nothing to index!")

                                else:
                                    application_logger.warning(
                                        f"No properties in node {str(node_id)}")
                        else:
                            application_logger.warning("No nodes...")
                else:
                    application_logger.warning("No available data")
            else:
                application_logger.warning("No results in the json file...")
            try:
                self.update_elastic_search_index(content_list, index_name)
                application_logger.warning("Refreshing index...")
                self.elsearch.indices.refresh(index=index_name)
            except Exception as e:
                application_logger.error(f"Error Updating the ElasticSearch index: {str(e)}")
                application_logger.error(f"Error Updating content: {str(content_list)} Index: {str(index_name)}")
                application_logger.error(e, exc_info=True)
        except Exception as e:
            application_logger.error(f"Error parsing a json dictionary and updating the ElasticSearch index: {str(e)}")
            application_logger.error(e, exc_info=True)

    def __aux_dbpedia_search(self, query_search, index_name, dataset_vector):
        """
        This function performs a search in the specified index using the provided query and dataset vector.
        
        Args:
            query_search (str): The search query.
            index_name (str): The name of the index to search in.
            dataset_vector (str): The name of the dataset vector field.
            
        Returns:
            list: A list of dictionaries containing the sentences and URIs of the search results.
        """
        uri_node_list = list()

        try:
            size_query = str(20)
            
            # Get word embeddings for the query
            dataset_embedding = config.semantic_search.get_word_embeddings(query_search).tolist()
            
            # Build the Elasticsearch query body
            body_query = {
                "size": size_query,
                "_source": {"excludes": ['dataset_vector', 'dataset_vector_es']},
                "query": {
                    "script_score": {
                        "query": {
                            "match_all": {}
                        },
                        "script": {
                            # Calculate the score using cosine similarity
                            "source": f"(1.0 + cosineSimilarity(params.{str(dataset_vector)}, '{str(dataset_vector)}'))/2.0",
                            "params": {
                                dataset_vector: dataset_embedding
                            }
                        }
                    }
                }
            }
            
            # Search in the specified index
            node_list = self.search_in_index(query_search, index_name, body_query)

            # Build the basic Elasticsearch query body
            body_query = self.calculate_basic_query_elastisearch(query_search, size_query)
            
            # Search in the consulting index
            node_list += self.search_in_index(query_search, self.consulting_index_name, body_query)

            # Extract the sentences and URIs from the search results
            uri_node_list = [{'sentence': node.get(self.dataset_text), 'uri': node.get('uri')} for node in node_list]

        except Exception as e:
            application_logger.error(f"Error searching on {str(index_name)} Query: {str(query_search)}")
            application_logger.error(e, exc_info=True)
        
        return uri_node_list

    ########################################################################
    #
    #   ALL INDEX
    #
    ######################################################################
    def create_elastic_search_index_all(self):
        """
        Creates all the necessary indexes for Elasticsearch.

        This function calls the create_elastic_search_index_consulting() and create_dbpedia_index() methods.
        """
        self.create_elastic_search_index_consulting()
        self.create_dbpedia_index()

    #############################################################################
    #
    #
    #   CONSULTING INDEX
    #
    ###########################################################################

    def search_in_index_consulting(self, query_search, size_query=1):
        """
        Search for documents in the consulting index based on a query.

        Args:
            query_search (str): The search query.
            size_query (int, optional): The number of documents to retrieve. Defaults to 1.

        Returns:
            list: A list of retrieved documents sorted by score.
        """
        # Remove leading and trailing whitespaces from the query
        query_str = query_search.strip()

        # Convert size_query to an integer
        size_query = int(size_query)

        # Get word embeddings for the query
        dataset_embedding = config.semantic_search.get_word_embeddings(query_str).tolist()

        # Create the Elasticsearch query body
        body_query = {
            "size": size_query,
            "min_score": 7.0,
            "_source": {"excludes": ['dataset_vector']},
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "(1.0 + cosineSimilarity(params.dataset_vector, 'dataset_vector'))/2.0 * 10.0",
                        "params": {
                            "dataset_vector": dataset_embedding
                        }
                    }
                }
            }
        }

        # Search for documents in the consulting index
        uri_node_list = self.search_in_index(query_str, self.consulting_index_name, body_query)

        # Calculate basic query for Elasticsearch
        body_query = self.calculate_basic_query_elastisearch(query_str, size_query)

        # Search for additional documents in the consulting index
        uri_node_list += self.search_in_index(query_str, self.consulting_index_name, body_query)

        # Parse the results of the query
        uri_node_list = self.parse_results_query(uri_node_list)

        # Sort the documents by score
        return self.sort_by_score(uri_node_list, size_query)

    def sort_by_score(self, original_list, size_query):
        """
        Sort a list of dictionaries by the 'score' key in descending order,
        and return the top 'size_query' number of items.

        Args:
            original_list (list): The original list of dictionaries to be sorted.
            size_query (int): The number of items to be returned.

        Returns:
            list: The sorted list of dictionaries.

        Raises:
            Exception: If there is an error while sorting the list.
        """
        uri_result_list = list()
        try:
            uri_result_list = sorted(original_list, key=lambda d: d['score'], reverse=True)
            if len(uri_result_list) > size_query:
                uri_result_list = uri_result_list[0:size_query]
        except Exception as e:
            application_logger.error(
                f"Error while sorting score datasets: {str(e)}")
            application_logger.error(e, exc_info=True)
        return uri_result_list

    def parse_results_query(self, original_list):
        """
        Auxiliary function whose purpose is to get the best doc in the 'original_list' parameter
        """
        parse_list = list()
        try:
            parse_list = list()
            index = 0
            while index < len(original_list):
                title_id = original_list[index].get('uri')
                found_element = False
                for element in parse_list:
                    id_element = element.get('uri')
                    if title_id.strip() == id_element.strip():
                        found_element = True
                        break
                if not found_element:
                    parse_list.append(original_list[index])
                index = index + 1
            # Remove the unnecessary docs
        except Exception as e:
            application_logger.error(
                f"Error parsing the results: {str(e)}")
            application_logger.error(e, exc_info=True)
        return parse_list

    def create_elastic_search_index_consulting(self):
        # Define the mapping for the Elasticsearch index
        es_index = {
            "mappings": {
                "properties": {
                    "dataset": {
                        "type": "text"
                    },
                    "dataset_vector": {
                        "type": "dense_vector",
                        "dims": 768
                    }
                }
            }
        }
        # Create the Elasticsearch index with the defined mapping
        self.create_elastic_search_index(self.consulting_index_name, es_index)

    def parse_dict_and_update_consulting(self, json_graph):
        self.parse_dict_and_update(json_graph, self.consulting_index_name)

    def update_elastic_search_index_consulting(self, datasets_dict):
        self.update_elastic_search_index(
            datasets_dict, self.consulting_index_name)

    ########################################################################################
    #
    #
    #
    # DBPEDIA INDEX
    #
    #
    #########################################################################################
    def create_dbpedia_index(self):
        """
        Creates an index in Elasticsearch for the DBpedia dataset.

        Returns:
            bool: True if the index was created successfully, False otherwise.
        """
        # Define the Elasticsearch index mapping
        es_index = {
            "mappings": {
                "properties": {
                    "dataset": {
                        "type": "text"
                    },
                    "dataset_vector": {
                        "type": "dense_vector",
                        "dims": 768
                    },
                    "dataset_vector_es": {
                        "type": "dense_vector",
                        "dims": 768
                    }
                }
            }
        }

        # Create the Elasticsearch index
        bool_new_index = self.create_elastic_search_index(self.dbpedia_index_name, es_index)
        # Update the DBpedia nodes if the index was created successfully
        if bool_new_index:
            self.update_dbpedia_nodes(self.dbpedia_index_name)

    def search_in_index_dbpedia(self, query_search):
        """
        Searches for a query in the DBpedia index.

        Args:
            query_search (str): The query to search for.

        Returns:
            str: The result of the search.
        """
        return self.__aux_dbpedia_search(query_search, self.dbpedia_index_name, "dataset_vector")

    ########################################################################################
    #
    #
    #
    # SPANISH DBPEDIA INDEX
    #
    #
    #########################################################################################

    def search_in_index_es_dbpedia(self, query_search):
        dataset_vector = "dataset_vector_es"
        return self.__aux_dbpedia_search(query_search, self.dbpedia_index_name, dataset_vector)

    def update_dbpedia_nodes(self, index_name=None):
        """
        Update the nodes in the DBpedia database.

        Args:
            index_name (str, optional): Name of the index to update. Defaults to None.
        """
        # Log the start of the extraction process
        application_logger.info("Extracting all classes from dbpedia local file...")

        # Create an empty list to store the extracted content
        content_list = list()

        dataset_content = pd.DataFrame()

        # Read the dataset from the dbpedia.tsv file
        dataset_content_1 = pd.read_csv(config.APP_INPUT_DATA + "dbpedia_1.tsv", header=None, sep=';', error_bad_lines=False)
                # Read the dataset from the dbpedia.tsv file
        dataset_content_2 = pd.read_csv(config.APP_INPUT_DATA + "dbpedia_2.tsv", header=None, sep=';', error_bad_lines=False)

        # Concatenate the two datasets
        dataset_content = pd.concat([dataset_content_1, dataset_content_2],axis=0).reset_index(drop=True)


        # Iterate over each row in the dataset
        for index, row in dataset_content.iterrows():
            try:
                # Extract the uri_class and spanish_label from the row
                uri_class = row[0].strip()
                spanish_label = row[1].strip()

                # Clean the spanish_label by removing extra spaces, parentheses, and newlines
                spanish_label = spanish_label.replace(r" [ ]+", " ")
                spanish_label = spanish_label.replace("(", "")
                spanish_label = spanish_label.replace(")", "")
                spanish_label = spanish_label.strip().replace(r"\n", "")

                # Extract the dbpedia_class from the uri_class and clean it
                dbpedia_class = row[0].strip()
                dbpedia_class = dbpedia_class.replace("http://dbpedia.org/resource/", "")
                dbpedia_class = dbpedia_class.replace("http://dbpedia.org/ontology/", "")
                dbpedia_class = utils.transform_class_name(dbpedia_class)
                dbpedia_class = dbpedia_class.replace(r" [ ]+", " ")
                dbpedia_class = dbpedia_class.replace("(", "")
                dbpedia_class = dbpedia_class.replace(")", "")
                dbpedia_class = dbpedia_class.strip().replace(r"\n", "")

                # Create a dictionary with the extracted values and add it to the content_list
                dict_node = {
                    'id': uri_class,
                    'es_content': spanish_label,
                    'content': dbpedia_class
                }
                content_list.append(dict_node)
            except Exception as e:
                # Log any errors that occur during the extraction process
                application_logger.error(f"Index: {str(index)} Row: {row}")
                application_logger.error(e, exc_info=True)

        try:
            # Update the elastic search dbpedia with the extracted content
            application_logger.info("Update index...")
            self.update_elastic_search_dbpedia(content_list, index_name)

            # Refresh the index
            application_logger.warning("Refreshing index...")
            self.elsearch.indices.refresh(index=index_name)

            # Log the completion of the extraction process
            application_logger.info("Extraction done!")
        except Exception as e:
            # Log any errors that occur during the update process
            application_logger.error(f"Error: {str(e)} Index name:{str(index_name)}")
            application_logger.error(e, exc_info=True)

    def calculate_basic_query_elastisearch(self, query, size_query):
        """
        Returns the Elasticsearch query that searches through the dataset's text 

        """
        body_query = {
            "size": size_query,
            "_source": {"excludes": ['dataset_vector']},
            "min_score": 7.0,
            "query": {
                "bool": {
                }

            }
        }
        if query and len(query) > 1:
            body_query["query"]["bool"]["must"] = [
                {"match": {self.dataset_text: query}},

            ]
        else:
            body_query["query"]["bool"]["must"] = {
                "match_all": {}
            }

        return body_query

    def update_elastic_search_dbpedia(self, datasets_dict, index_name):
        """
        Updates the index with new datasets.
        """
        self.mutex.acquire()
        try:
            application_logger.info(
                f"Updating index -> {str(len(datasets_dict))}")
            for dataset in datasets_dict:
                dataset_content = dataset.get('content')
                node_id = dataset.get('id')
                spanish_content = dataset.get('es_content')
                if dataset_content and node_id:
                    try:
                        embbeded_dataset = config.semantic_search.get_word_embeddings(
                            dataset_content).tolist()
                        embbeded_spanish = config.semantic_search.get_word_embeddings(
                            spanish_content).tolist()
                        doc = {
                            "dataset": dataset_content,
                            "dataset_vector": embbeded_dataset,
                            "dataset_vector_es": embbeded_spanish
                        }
                        res = self.elsearch.index(
                            index=index_name, id=node_id, body=doc)
                    except Exception as e:
                        application_logger.error(
                            f"Exception caught -> {str(e)}")
                        application_logger.error(
                            f"Error while indexing -> {str(dataset_content)}   <-> {str(node_id)}")
                        application_logger.error(e, exc_info=True)

        except Exception as e:
            error_message=f"Error while updating: {str(e)} Index name:{str(index_name)} Dataset: {str(datasets_dict)}"
            application_logger.error(error_message)
            application_logger.error(e, exc_info=True)
        self.mutex.release()
