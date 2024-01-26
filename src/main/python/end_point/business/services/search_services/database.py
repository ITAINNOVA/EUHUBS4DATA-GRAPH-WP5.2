

from py2neo import Graph
from end_point.logging_ita import application_logger
import requests
from end_point.business import utils
import end_point.config as config
import threading
# How to solve Neo4j logging vulnerability
# https://community.neo4j.com/t/log4j-cve-mitigation-for-neo4j/48856
# How to install neo4j 4:1
# https://askubuntu.com/questions/92019/how-to-install-specific-ubuntu-packages-with-exact-version
# https://www.cyberciti.biz/faq/debian-ubuntu-linux-apt-get-aptitude-show-package-version-command/
# Installing Neo4j
# Security on Neo4j
# https://neo4j.com/docs/http-api/current/security/
# Authenticate by sending a username and a password to Neo4j using HTTP Basic Auth. Requests should include an Authorization header,
# with a value of Basic <payload>, where "payload" is a base64 encoded string of "username:password".


class DatabaseConnector():
    """
    Class used to interact with the database.
    Provides methods to import and exports nodes to Neo4j.
    """

    def __init__(self):
        self.mutex = threading.Lock()

        self.connection_db = Graph(
            scheme='bolt', host=config.DB_DATABASE, port=config.DB_PORT_DB, auth=(config.DB_USERNAME, config.DB_PASSWORD))

        application_logger.info('Creating database...')
        application_logger.warning('It will fail if the database already exists. However, do not worry about it.')
        self.run_query('CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE')

        application_logger.info('Starting configuration')
        warning_message = """
        Do not worry if you see errors during this configuration step.
        Your database perhaps already has some configuration.
        So it will failed if it is attempted to be reconfigured.
        """
        application_logger.warning(warning_message)
        self.run_query(
            'CALL n10s.graphconfig.init({keepLangTag: true, handleMultival: "ARRAY", handleVocabUris: "KEEP"})')

        self.run_query(
            'CALL n10s.nsprefixes.add("dcat", "http://www.w3.org/ns/dcat#");')
        self.run_query(
            'CALL n10s.nsprefixes.add("dct", "http://purl.org/dc/terms/");')
        self.run_query(
            'CALL n10s.nsprefixes.add("foaf","http://xmlns.com/foaf/0.1/");')
        self.run_query(
            'CALL n10s.nsprefixes.add("sch","http://schema.org/");')
        self.run_query(
            'CALL n10s.nsprefixes.add("owl","http://www.w3.org/2002/07/owl#");')
        self.run_query(
            'CALL n10s.nsprefixes.add("ids","https://w3id.org/idsa/core/");')
        self.run_query(
            'CALL n10s.nsprefixes.add("adms","http://www.w3.org/ns/adms#");')
        self.run_query(
            'CALL n10s.nsprefixes.add("time","http://www.w3.org/2006/time");')
        self.run_query(
            'CALL n10s.nsprefixes.add("dbpedia","http://dbpedia.org/resource/");')

    def request_current_node_in_database(self, class_node, class_property, new_node_title):
        """Request the URI of a node on the database and returns its uri in case it could find it
        """
        result = None
        try:
            query = f"MATCH (n:`{str(class_node)}`) WHERE  ANY(s IN n.`{str(class_property)}` WHERE s =~ '.*{str(new_node_title)}.*') RETURN n.uri"
            result = self.run_query(query)
            if type(result) is list and len(result) > 0:
                result = result[0]
                result = result.get('n.uri')
        except Exception as e:
            application_logger.error(
                f"Exception caugth while requesting current node in database: {str(e)}")
            application_logger.error(e, exc_info=True)
        return result

    def request_all_instances_class(self, class_name):
        """ Request all the instance of a class to the remote database

        Args:
            class_name ([str]): URI of the class

        Returns:
            [List]: Returns an list of instance of the requested class
        """
        instance_list = list()
        try:
            query = f"MATCH (n:`{str(class_name)}`) RETURN n,n.uri"
            result = self.run_query(query)
            for instance in result:
                uri = instance.get('n.uri')
                node_ins = instance.get('n')
                instance_dictionary = dict(node_ins)
                instance_list.append((uri, instance_dictionary))
        except Exception as e:
            application_logger.error(
                f"Exception caugth while requesting all instances: {str(e)}")
            application_logger.error(e, exc_info=True)
        return instance_list

    def remote_import_file(self, path_file, content_type):
        """
        Import rdf file in neo4j database:
            https://neo4j.com/labs/neosemantics/

        """
        result = None
        self.mutex.acquire()
        try:

            query = f"CALL n10s.rdf.import.fetch('{path_file}', '{content_type}');"
            response = self.run_query(query)

            if type(response) is list:
                response = response[0]

            application_logger.info(response)
            result = response.get('terminationStatus')

        except Exception as e:
            application_logger.error(
                f'Exception caught while importing file: {str(e)}')
            application_logger.error(e, exc_info=True)
        self.mutex.release()
        return result

    def request_all_node_information(self, uri):
        """ Request the information and relationships in which the node with
            the same uri as URI (parameter) is involved.

        Args:
            uri (str): URI of the node

        Returns:
            dictionary : JSON dictionary with the node information in Neo4j graph format
        """
        # Tutorial: https://chowdera.com/2021/08/20210826195400318e.html
        # How to use py2neo to query nodes, relationships, and paths in neo4j
        query = f'MATCH (n) WHERE n.uri ="{str(uri)}" OPTIONAL MATCH (n)-[r]-(m) WHERE n.uri ="{str(uri)}" RETURN n,r,m;'
        return self.__query__result_as_graph(query)

    def request_the_whole_database(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-(m) RETURN n,r,m;"
        return self.__query__result_as_graph(query)

    def run_query(self, query):
        """
        Executes a query on the neo4j database.
        """
        result = []
        try:
            result = self.connection_db.run(query).data()
        except Exception as e:
            application_logger.error(
                f'Exception caught while running query on database: {str(e)}')
            application_logger.error(e, exc_info=True)

        return result

    def extract_all_nodes_as_graph(self, list_uris):
        """Given a list of URIs this function will extract all the nodes
        whose uri is in the list given as a parameter

        Args:
            list_uris (List<str>):List of Neo4j nodes' uris

        Returns:
            dictionary : JSON dictionary with the node information in Neo4j graph format
        """
        query = f'MATCH (n) WHERE n.uri IN {str(list_uris)} OPTIONAL MATCH (n)-[r]->(m) WHERE n.uri IN {str(list_uris)} RETURN n,r,m;'
        return self.__query__result_as_graph(query)

    def __query__result_as_graph(self, query):
        """
        Tutorial:   Return results in graph format
                    https://neo4j.com/docs/http-api/current/actions/return-results-in-graph-format/
        """
        request_body = {
            "statements": [
                {
                    "statement": query,
                    "resultDataContents": ["graph"]
                }
            ]
        }
        authorization = "Basic " + \
            str(utils.basencode54(config.DB_USERNAME + ":"+config.DB_PASSWORD))
        newHeaders = {'Content-type': 'application/json;charset=UTF-8',
                      'Accept': 'application/json', 'Authorization': authorization}
        url_post = "http://"+str(config.DB_DATABASE) + ":" + \
            str(config.NEO4J_HTTP_PORT)+"/db/neo4j/tx/commit"
        response = requests.post(
            url_post, json=request_body, headers=newHeaders)

        return (response.json())
