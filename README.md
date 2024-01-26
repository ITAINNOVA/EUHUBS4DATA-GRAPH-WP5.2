# EUHUBS4DATA TASK 5.2
## RUN APPLICATION
Run the following command:
```bash
bash src/main/script/start.sh
```
## STOP APPLICATION
Run the following command:
```bash
bash src/main/script/stop.sh
```

## HOW SEE APPLICATION LOGS
Run the following command:
```bash
bash src/main/script/app.sh -l
```

### Technologies in this project:
- ElasticSearch (https://www.elastic.co/es/what-is/elasticsearch)
- Neo4j (https://neo4j.com/)
- Flask Application (https://flask.palletsprojects.com/en/2.0.x/)

## DEPENDENCIES
Currently this project has some dependencies worth remarking:
### Python library dependencies  

It depends on **py2neo** library, although this library has been deprecated and no longer has supported by their former creators, there is a stable version available on [GitHub Py2Neo](https://github.com/overhangio/py2neo/releases/download/2021.2.3/py2neo-2021.2.3.tar.gz). This library is already in the Docker image, installed during the building process of the Docker image.  
Two transformers libraries are needed: 
- sentence-transformers==2.1.0 [Python SentenceTransformers](https://www.sbert.net/)
- transformers==4.13.0  [Python Transformers](https://huggingface.co/docs/transformers/index)

For connecting the python application with **ElasticSearch** the drivers library must be installed: 
- elasticsearch==7.16.3 [Python Elasticsearch Client](https://elasticsearch-py.readthedocs.io/en/v7.16.0/)

#### OQUARE WEBSITES
A module to automatically obtain metrics from ontology files based of **OQuaRE framework** for ontology quality evaluation, generating visual reports which showcase the quality of each ontology.  
- http://sele.inf.um.es/oquare
- https://github.com/Emdien/oquare-metrics
- https://github.com/Emdien/oquare-metrics/blob/master/src/force.sh
- http://semantics.inf.um.es:8080/oquare-ws/rest/corpus  

Jar files of java oquare library is located in the path *./src/main/java/oquare-versions.jar* . Project developed by a student of [Universidad de Murcia](https://www.um.es/) access granted by professor [Jesualdo Tomas Fernandez Breis](https://webs.um.es/jfernand/miwiki/doku.php).

## Machine learning models

As its python application can process also text in Spanish it needs **Wordnet** database for Spanish language. It can be found at the URL: https://github.com/pln-fing-udelar/intropln2013-lab2/tree/master/wordnet_spa   

In relation to the language models uses for analyzing text and extracting entities. This is the list of used models: 
- https://huggingface.co/xlm-roberta-large-finetuned-conll03-english 
- https://huggingface.co/dccuchile/bert-base-spanish-wwm-uncased 
- https://huggingface.co/bert-base-uncased 
- https://huggingface.co/Helsinki-NLP/opus-mt-es-en 

All of them are available on **GitHub** so in order to run this project **HuggingFace** credentials are required. **SpaCy library** is also on the requirements file, and it uses their medium size models for English and Spanish: 
- **English Model**: https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.2.0/en_core_web_md-3.2.0-py3-none-any.whl 
- **Spanish Model**: https://github.com/explosion/spacy-models/releases/download/es_core_news_md-3.2.0/es_core_news_md-3.2.0-py3-none-any.whl 

## Docker Images 
- neo4j:4.4.3 
- elasticsearch: 7.16.3 

## Disk capacity 
The host machine for development has a disk memory of 295G and is used 118G. 42% of the total disk memory.  

## CKAN dependency 

After processing the raw text and creating the database graph this python application load datasets on a CKAN URL, in this case: https://euh4d-data-portal.vm.fedcloud.eu/ 

For this specific CKAN instance an API key is required. It has to be included in requests header. 
```bash
{'Authorization': "CKAN_API_KEY"} 
```

## Web application domain 

Currently the domain is: https://euhub4data-graphs.itainnova.es 

## Application credentials
In file *docker-compose.yml* environment variables are declared to be used for the application. **Docker-compose** reads environmnet variables from the file *./src/main/docker/.env*, in case it is not created, create it.  These variables must be declared in the host machine so this can run.

Database credentials
```python
NEO4J_USER=""
NEO4J_DB_PORT=7687
NEO4J_PASS=""
NEO4J_DB_HTTP_PORT=7474
```
CKAN API key 
```python
CKAN_HOST="https://euh4d-data-portal.vm.fedcloud.eu"
CKAN_API_KEY=""
```
Elasticsearch credentials 
```python
ELASTICH_SEARCH_PORT=9200
ELASTIC_USER="elastic"
ELASTIC_PASSWORD=""
```
Flask application port
```python
FLASK_APP_PORT=5001
```
Docker compose host configuration
```python
DB_DATABASE="neo4j-db"
HOST_NAME="ontology_front_tool"
ELSE_HOST="elastic-search"
TZ="Europe/Madrid"
LOGLEVEL="DEBUG"
```

## Hardware recommendations
To ensure the optimal performance and stability of the project, the following infrastructure specifications are required: 
### Computing Resources 
- **CPU:** Minimum of an 8-core processor. 
- **RAM:** At least 24 GB. 

### Software Dependencies 
The Python application associated with this project is containerized using Docker and docker-compose. Therefore, the host machine must have Docker and docker-compose installed. Python version 3.8.10. 

### Recommended Versions 
- **Docker:** Version 23. 
- **docker-compose:** Version 1.29. 
- **Operating System:** The system should be running Ubuntu 20.04. 

## Ontologies involved in this project

- World Wide Web Consortium: https://www.w3.org/ns/org
- Friend Of A Friend Ontology http://xmlns.com/foaf/spec/index.rdf
- Dublin Core Terms; https://www.dublincore.org/resources/glossary/ontology/
- EUR-Lex European Law Ontology: https://eur-lex.europa.eu/homepage.html
- The data cube ontology: http://purl.org/linked-data/cube
- Schema.org Ontology: http://schema.org/
