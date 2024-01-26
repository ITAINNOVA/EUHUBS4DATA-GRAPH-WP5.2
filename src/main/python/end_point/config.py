import os
from end_point.business.services.semantic.semantic_similarity import SemanticSimilarity
from end_point.business.services.semantic.syns_maker import SynsMaker
from end_point.business.services.semantic.translator import TranslatorMarian
import end_point.business.cache.cache_db as cache
from rdflib.namespace import DCTERMS, Namespace, OWL, DCTERMS

APP_ROOT = str(os.environ.get('APP_ROOT',os.path.dirname(os.path.abspath("~/.."))))
JAVA_PATH_JAR=os.environ.get('JAVA_PATH_JAR',"./src/main/java/")
APP_RESOURCES = os.path.join(APP_ROOT, "resources/")
APP_ONTOLOGY = os.path.join(APP_RESOURCES, "ontology/")
APP_INPUT_DATA = os.path.join(APP_RESOURCES, "data/")
APP_INPUT_OQUARE = os.path.join(APP_RESOURCES, "oquare/")
APP_END_POINT = os.path.join(APP_ROOT,"end_point/")

TEMPLATE_PATH = os.path.join(APP_ROOT,'templates/' )
STATICS_PATH = os.path.join(APP_ROOT,'static/' ) #

EXTENDED_ONTOLOGY = "ids_core_main_ontology_modified.ttl"
EXTENDED_IDS_ONTOLOGY_PATH = os.path.join(APP_ONTOLOGY, EXTENDED_ONTOLOGY)

adjectives_file_path = os.path.join(os.path.dirname(APP_RESOURCES), 'data/english-adjectives.txt')
adverbs_file_path = os.path.join(os.path.dirname(APP_RESOURCES), 'data/adverbs.txt')
spanish_stopwords_path = os.path.join(os.path.dirname(APP_RESOURCES), 'data/spanish_stopwords.txt')

UPDATED_ONTOLOGY_FILE_NAME = "ontology_updated"
CREATE_JSON_FILE = "new_json_file"

DB_USERNAME = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASS')
DB_DATABASE = os.environ.get('DB_DATABASE',"0.0.0.0")
# NEO4J_DB_PORT
DB_PORT_DB = os.environ.get('NEO4J_DB_PORT',7687)
HOST_NAME = os.environ.get('HOST_NAME',"0.0.0.0")
ELASTIC_NODE = os.environ.get('ELSE_HOST',"0.0.0.0")
DIR_WORDNET_SPA = os.environ.get('DIR_WORDNET_SPA','~/nltk_data/corpora/wordnet_spa')

CKAN_HOST = os.environ.get('CKAN_HOST')
CKAN_API_KEY = os.environ.get('CKAN_API_KEY')
CKAN_ORGANIZATION = "euhubs4data"

ELASTIC_USER = os.environ.get('ELASTIC_USER')
ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD')

OQUARE_XML_FILE = os.path.join(os.path.dirname(APP_INPUT_OQUARE,), 'oquareResult_IDS.xml')
OQUARE_BASE_XML = os.path.join(os.path.dirname(APP_INPUT_OQUARE), 'oquareResult_BASE.xml')
OQUARE_IDS_XML = os.path.join(os.path.dirname(APP_INPUT_OQUARE), 'oquareResult_COMPLETE.xml')

NEO4J_HTTP_PORT =os.environ.get('NEO4J_DB_HTTP_PORT',7474)
ENGLISH_SPACY_NER = 'en_core_web_md'
IDS_CORE_FORMAT = 'Turtle'
MAIN_ONTOLOGY_FILE = 'ids_core_main_ontology.ttl'
IDS_CORE_FORMAT_LOW_CHARACTERS = 'turtle'
DCAT_MAIN_ONTOLOGY = 'dcat_main_ontology.ttl'
DCAT_CORE_MAIN = "http://www.w3.org/ns/dcat"
PROPERTY_DESCRIPTION = "description"
PROPERTY_TITLE = "name"
CKAN_HOST = "https://euh4d-data-portal.vm.fedcloud.eu/"
IDS_CORE_URL = 'https://international-data-spaces-association.github.io/InformationModel/docs/serializations/ontology.ttl'
IDS_CORE_MAIN_ONTOLOGY = "https://w3id.org/idsa/core/"

PRETTY_FORMAT = "pretty-xml"
NODE_PROPERTY_NAME = DCTERMS.title
found_invalid = [
    'and', 'of', 'in', 'to', ',', 'for', 'by', 'with', 'on', 'as', 'that', 'from', ')', '(', 'which',
    'at', ';', 'or', 'but', 'the', 'not', 'after', '"', 'include', 'also',
    'into', 'between', 'such', ':', 'do', 'while', 'when', 'during', 'would', 'over', 'since', '2019',
    'well', 'than', '2020', 'under', 'where', 'one', 'hold', '2018', 'can', 'through', '-',
    'out', 'there', 'know', 'due', 'a', 'up', 'before', 'about',
    "'",  '4', '10', '3', '11', '&', '$', '12',  '2015', '2008', '–', 'will',
    'so', 'do', 'follow', 'most', 'although', 'cause', 'only', '—',  '2007',  '2014', 'mostly', '5', 'say', '2017', '20',
    '2009'
]

invalid_relations = [
    'and', 'but', 'or', 'so', 'because', 'when', 'before', 'although',  # conjunction
    'oh', 'wow', 'ouch', 'ah', 'oops',
    'what', 'how', 'where', 'when', 'who', 'whom',
    'a', 'and', 'the', 'there', ',', ' ', ';',
    'them', 'he', 'she', 'him', 'her', 'it',  # pronoun
    'ten', 'hundred', 'thousand', 'million', 'billion',  # unit
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',  # number
    'year', 'month', 'day', 'daily'
] + found_invalid

auxiliaries = [
    'can', 'dare', 'may', 'will', 'would', 'should',
    'need', 'ought', 'shall', 'might', 'do', 'does', 'did',
    'be able to', 'had better', 'have to', 'need to', 'ought to', 'used to'
]

with open(adjectives_file_path, 'r') as f:
    adjectives = [line.strip().lower() for line in f]

with open(adverbs_file_path, 'r') as f:
    adverbs = [line.strip().lower() for line in f]


invalid_relations += adjectives
invalid_relations += adverbs

invalid_relations_es = []

with open(spanish_stopwords_path, 'r') as f:
    invalid_relations_es = [line.strip().lower() for line in f]

invalid_characters = ['{', '}', '[', ']', ',',
                      '.', ':', ';', '/', '&', '$', '#', '@']

invalid_relations += invalid_characters
invalid_relations_es += invalid_characters

db_cache = cache.CacheDB()
ids_db_cache = cache.CacheDB()
base_ids_db_cache = cache.CacheDB()

semantic_search = SemanticSimilarity()
syns_maker = SynsMaker(DIR_WORDNET_SPA)
translator = TranslatorMarian("es", "en")

invalid_relations_set_en = set(invalid_relations)
invalid_relations_set_es = set(invalid_relations_es)


ONTOLOGY_PREFIX = {
    "owl": OWL,
    "time": Namespace("http://www.w3.org/2006/time#"),
    "dc": Namespace("http://purl.org/dc/elements/1.1/"),
    "ns": Namespace("http://www.w3.org/2006/vcard/ns#"),
    "rdf": Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    "xml": Namespace("http://www.w3.org/XML/1998/namespace"),
    "xsd": Namespace("http://www.w3.org/2001/XMLSchema#"),
    "a-cd": Namespace("https://w3id.org/arco/ontology/context-description/"),
    "a-ce": Namespace("https://w3id.org/arco/ontology/cultural-event/"),
    "a-dd": Namespace("https://w3id.org/arco/ontology/denotative-description/"),
    "arco": Namespace("https://w3id.org/arco/ontology/arco/"),
    "core": Namespace("https://w3id.org/arco/ontology/core/"),
    "dcat": Namespace("http://www.w3.org/ns/dcat#"),
    "foaf": Namespace("http://xmlns.com/foaf/0.1/"),
    "opla": Namespace("http://ontologydesignpatterns.org/opla#"),
    "prov": Namespace("http://www.w3.org/ns/prov#"),
    "rdfs": Namespace("http://www.w3.org/2000/01/rdf-schema#"),
    "a-cat": Namespace("https://w3id.org/arco/ontology/catalogue/"),
    "a-loc": Namespace("https://w3id.org/arco/ontology/location/"),
    "opla1": Namespace("http://ontologydesignpatterns.org/opla/"),
    "ids": Namespace("https://w3id.org/idsa/core/"),
    "code": Namespace("https://w3id.org/idsa/code/"),
    "ns": Namespace("http://creativecommons.org/ns#"),
    "odrl": Namespace("http://www.w3.org/ns/odrl/2/"),
    "ids0": Namespace("https://w3id.org/idsa/core/0,"),
    "vann": Namespace("http://purl.org/vocab/vann/"),
    "idsm": Namespace("https://w3id.org/idsa/metamodel/"),
    "dcam": Namespace("http://purl.org/dc/dcam/"),
    "xsd": Namespace("http://www.w3.org/2001/XMLSchema#"),
    "skos": Namespace("http://www.w3.org/2004/02/skos/core#"),
    "scovo": Namespace("http://purl.org/NET/scovo#"),
    "void": Namespace("http://rdfs.org/ns/void#"),
    "qb": Namespace("http://purl.org/linked-data/cube#"),
    "dcterms": Namespace("http://purl.org/dc/terms/"),
    "freq": Namespace('http://purl.org/cld/freq'),
    "docs": Namespace('https://postgis.net/docs'),
    "locn": Namespace('http://www.w3.org/ns/locn'),
    "geo": Namespace('http://www.geonames.org/ontology'),
    "dbp": Namespace('http://dbpedia.org/resource'),
    "voaf": Namespace('http://purl.org/vocommons/voaf'),
    "url": Namespace('https://www.gnu.org/software/emacs/manual/html_node/url')
}

STATS_LABELS = ["LCOMOnto", "WMCOnto2", "DITOnto", "NACOnto", "NOCOnto", "CBOOnto",
                "RFCOnto", "NOMOnto", "RROnto", "PROnto", "AROnto", "INROnto", "ANOnto", "TMOnto2"]

BASE_IDS_ONTOLOGY_PATH = os.path.join(APP_ONTOLOGY, MAIN_ONTOLOGY_FILE)

COUNTRIES_KEY_NAME = [
    {'key': 'Austria', 'name': 'Austria'},
    {'key': 'Belgium', 'name': 'Belgium'},
    {'key': 'Croatia', 'name': 'Croatia'},
    {'key': 'Czech Republic', 'name': 'Czech Republic'},
    {'key': 'Denmark', 'name': 'Denmark'},
    {'key': 'Estonia', 'name': 'Estonia'},
    {'key': 'EU-wide', 'name': 'EU-wide'},
    {'key': 'Finland', 'name': 'Finland'},
    {'key': 'France', 'name': 'France'},
    {'key': 'Germany', 'name': 'Germany'},
    {'key': 'Greece', 'name': 'Greece'},
    {'key': 'Hungary', 'name': 'Hungary'},
    {'key': 'Iceland', 'name': 'Iceland'},
    {'key': 'Ireland', 'name': 'Ireland'},
    {'key': 'Italy', 'name': 'Italy'},
    {'key': 'Malta', 'name': 'Malta'},
    {'key': 'Netherlands', 'name': 'Netherlands'},
    {'key': 'Norway', 'name': 'Norway'},
    {'key': 'Poland', 'name': 'Poland'},
    {'key': 'Portugal', 'name': 'Portugal'},
    {'key': 'Romania', 'name': 'Romania'},
    {'key': 'Serbia', 'name': 'Serbia'},
    {'key': 'Slovak Republic', 'name': 'Slovak Republic'},
    {'key': 'Slovenia', 'name': 'Slovenia'},
    {'key': 'Spain', 'name': 'Spain'},
    {'key': 'Sweden', 'name': 'Sweden'},
    {'key': 'Switzerland', 'name': 'Switzerland'},
    {'key': 'Turkey', 'name': 'Turkey'},
    {'key': 'United Kingdom', 'name': 'United Kingdom'}
]

FIELDS_KEY_NAME = [
    {'key': 'Agriculture, Fisheries, Forestry and Food',
            'name': 'Agriculture, Fisheries, Forestry and Food'},
    {'key': 'Bioinformatics, Astronomy, and Earth Science',
            'name': 'Bioinformatics, Astronomy, and Earth Science'},
    {'key': 'Business', 'name': 'Business'},
    {'key': 'Economy and Finance', 'name': 'Economy and Finance'},
    {'key': 'Education, Culture and Sport',
            'name': 'Education, Culture and Sport'},
    {'key': 'Employment', 'name': 'Employment'},
    {'key': 'Employment, Treasury, Tourism, Urban planning and infraestructure, Housing, Society and welfare',
            'name': 'Employment, Treasury, Tourism, Urban planning and infraestructure, Housing, Society and welfare'},
    {'key': 'Energy', 'name': 'Energy'},
    {'key': 'Environment', 'name': 'Environment'},
    {'key': 'Geospatial Data', 'name': 'Geospatial Data'},
    {'key': 'Government and Public Sector',
            'name': 'Government and Public Sector'},
    {'key': 'Health', 'name': 'Health'},
    {'key': 'Housing and Zoning', 'name': 'Housing and Zoning'},
    {'key': 'Housing, planning and infraestructures',
            'name': 'Housing, planning and infraestructures'},
    {'key': 'Industry', 'name': 'Industry'},
    {'key': 'International Issues', 'name': 'International Issues'},
    {'key': 'Justice, Legal System and Public Safety',
            'name': 'Justice, Legal System and Public Safety'},
    {'key': 'Population and Society', 'name': 'Population and Society'},
    {'key': 'Regions and Cities', 'name': 'Regions and Cities'},
    {'key': 'Science and Technology', 'name': 'Science and Technology'},
    {'key': 'Social media', 'name': 'Social media'},
    {'key': 'Tourism', 'name': 'Tourism'},
    {'key': 'Tourism, mobility', 'name': 'Tourism, mobility'},
    {'key': 'tourism, security, sport, participation and public opinion',
            'name': 'tourism, security, sport, participation and public opinion'},
    {'key': 'Transport', 'name': 'Transport'},
    {'key': 'Water consumption', 'name': 'Water consumption'},
    {'key': 'Welfare', 'name': 'Welfare'}
]
URL_IDS_CORE_MAIN_MODIFIED = "https://euhub4data-graphs.itainnova.es/get-rdf/ids_core_main_ontology_modified.ttl"
URL_IDS_CORE_MAIN = "https://euhub4data-graphs.itainnova.es/get-rdf/ids_core_main_ontology.ttl"
JOYCE_URL ="https://cm.iti.es/api/integrations/datasets-metadata"

# Flask settings
FLASK_DEBUG =  True # Do not use debug mode in production
# Flask-Restplus settings
RESTX_SWAGGER_UI_DOC_EXPANSION = "list"
RESTX_VALIDATE = True
RESTX_MASK_SWAGGER = False
RESTX_ERROR_404_HELP = False