from rdflib import URIRef, Namespace, FOAF
from rdflib.plugins.sparql import prepareQuery

class SparqlQuery:

    # Query examples
    def __init__(self, graph, ontology_prefix):
        self.ontology_prefix = Namespace(str(ontology_prefix))
        self.graph = graph

    def get_all_attributes_instance_class(self, individual_uri):
        """Get all attributes contains by an instance from a graph ( or ontology).

        Args:
            individual_uri (URIRef): Uri which identifies an instance

        Returns:
            list: Returns a list composed by all the attributes of a class
        """
        q = prepareQuery(
            "SELECT DISTINCT ?property ?value WHERE { ?subject ?property ?value . }",
            initNs={"ids": self.ontology_prefix}
        )
        individual_uri = URIRef(individual_uri)
        qres = self.graph.query(q, initBindings={'subject': individual_uri})

        d = {}
        for row in qres:
            d[row.property.toPython()] = row.value.toPython()
        return d

    def get_all_instances_class(self, class_name):
        """ Get all instances of a class from a graph (or ontology)
        """
        q = prepareQuery(
            "SELECT DISTINCT ?subject WHERE { ?subject a ?classname . }",
            initNs={"ids": self.ontology_prefix})

        individual_uri = URIRef(class_name)
        qres = self.graph.query(q, initBindings={'classname': individual_uri})
        result = list()
        for row in qres:
            uri_instance = str(row.subject)
            properties_dict = self.get_all_attributes_instance_class(
                uri_instance)
            result.append((uri_instance, properties_dict))
        return result

    def get_all_properties(self, hide_implicit_preds=True):
        """
        Get all properties from a graph (or ontology).
        """
        query = """ 
                SELECT ?x ?c ?d
                WHERE {
                        {
                            { ?x a rdf:Property }
                            UNION
                            { ?x a owl:ObjectProperty }
                            UNION
                            { ?x a owl:DatatypeProperty }
                            UNION
                            { ?x a owl:AnnotationProperty }
                            %s
                        } .
                        OPTIONAL {
                            ?x a ?c 
                        }
                        OPTIONAL {
                            ?x rdfs:range ?d
                        }    
                        FILTER(!isBlank(?x)) .
                        } ORDER BY ?c ?x
                """
        BIT_IMPLICIT_PREDICATES = """union { ?a ?x ?b }"""
        if hide_implicit_preds:
            BIT_IMPLICIT_PREDICATES = ""
        query = query % BIT_IMPLICIT_PREDICATES
        qres = self.graph.query(query)
        result = list(qres)
        return result
