
from end_point.business import utils
from sentence_transformers import SentenceTransformer, util
from rdflib.namespace import DCTERMS
import os

class SemanticSimilarity:

    """
    Sematch is measuring semantic similarity based on taxonomies. 
    Sematch extends the NLTK version of WordNet and similarities with lemmatization, 
    multilingual support Open Multilingual WordNet and more semantic similarity metrics 
    into a single class WordNetSimilarity. 
    See information in: 
        https://pypi.org/project/sematch
        https://github.com/gsi-upm/sematch   
        https://gsi-upm.github.io/sematch/similarity
    Those metric names and their corresponding publications are listed as below.
        - path: Rada, Roy, et al. "Development and application of a metric on semantic nets." IEEE transactions on systems, man, and cybernetics 19.1 (1989): 17-30.
        - lch: Leacock, Claudia, and Martin Chodorow. "Combining local context and WordNet similarity for word sense identification." WordNet: An electronic lexical database 49.2 (1998): 265-283.
        - wup: RELACIONES DE LA TRIPLETAS -> Wu, Zhibiao, and Martha Palmer. "Verbs semantics and lexical selection." Proceedings of the 32nd annual meeting on Association for Computational Linguistics. Association for Computational Linguistics, 1994.
        - li: Li, Yuhua, Zuhair A. Bandar, and David McLean. "An approach for measuring semantic similarity between words using multiple information sources." IEEE Transactions on knowledge and data engineering 15.4 (2003): 871-882.
        - res: Resnik, Philip. "Using information content to evaluate semantic similarity in a taxonomy." arXiv preprint cmp-lg/9511007 (1995).
        - lin: Lin, Dekang. "An information-theoretic definition of similarity." ICML. Vol. 98. No. 1998. 1998.
        - jcn: Jiang, Jay J., and David W. Conrath. "Semantic similarity based on corpus statistics and lexical taxonomy." arXiv preprint cmp-lg/9709008 (1997).
        - wpath: Ganggao Zhu, and Carlos A. Iglesias. "Computing Semantic Similarity of Concepts in Knowledge Graphs." IEEE Transactions on Knowledge and Data Engineering 29.1 (2017): 72-85.

        Using a multilingual model:
        https://huggingface.co/sentence-transformers/paraphrase-xlm-r-multilingual-v1
        Previous model used: https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L6-v2
        Multilingual model: https://huggingface.co/sentence-transformers/paraphrase-xlm-r-multilingual-v1
                            http://xmlns.com/foaf/spec/index.rdf,http://xmlns.com/foaf/0.1/,RDF/XML,xml

    """

    def __init__(self):
        self.model = SentenceTransformer(os.environ.get("PARAPHRASE_XML_MODEL",'sentence-transformers/paraphrase-xlm-r-multilingual-v1'))

    def word_similarity_from_list(self, query, candidates_list):
        """
        Compute semantic similarity scores of a word  to a list of candidate and return the id
        of the highest score candidate and its score
        :param candidates_list List of candidates name to get the most similar to param query the uri
        """

        # By using transformer model get the most similar word the it can be
        candidates_len = len(candidates_list)
        embeddings1 = self.model.encode([query], convert_to_tensor=True)
        candidate_score = 0
        candidate_id = None
        # This function has returned the index of the name with the highest
        # similarity score
        # https://www.sbert.net/examples/applications/paraphrase-mining/README.html
        for i in range(candidates_len):
            # Compute embedding for the candidates list
            embeddings2 = self.model.encode(
                [candidates_list[i].lower()], convert_to_tensor=True)
            score = self.compute_cosine_scores(embeddings1, embeddings2)
            # Get the highest score
            if score > candidate_score:
                candidate_id = i
                candidate_score = score
        return candidate_id, candidate_score

    def word_similarity_compare(self, word1, word2):
        """
        Compute semantic similarity scores of two words by using transformers model.
        """
        embeddings1 = self.model.encode(word1.lower(), convert_to_tensor=True)
        embeddings2 = self.model.encode(word2.lower(), convert_to_tensor=True)
        return self.compute_cosine_scores(embeddings1, embeddings2)

    def get_word_embeddings(self, word):
        """
        Get the word embeddings for a given word.

        Args:
            word (str): The word to get embeddings for.

        Returns:
            numpy.ndarray: The word embeddings.
        """
        return self.model.encode(word)

    def compute_cosine_scores(self, embeddings1, embeddings2):
        """
        Compute the cosine score of two embeddings and return its value
        :params embeddings of two words 
        :return The value of the score for embeddings1 and embeddings2
        """
        # Compute cosine-similarits
        cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)
        # The tensor is on the GPU. In order to convert it to a NumPy array, you need to have the tensor on the CPU
        # https://stackoverflow.com/questions/61964863/typeerror-cant-convert-cuda0-device-type-tensor-to-numpy-use-tensor-cpu-to
        score = cosine_scores.cpu().numpy()[0][0]
        return score

    def find_best_option(self, value, query, uri_candidate, highest_score, sim_threshhold_content):
        """ Given the current best comparing score and threshhold return the uri of the
            instances in the database with the highest cosine score.

        Args:
            value ([str]): 
            query ([str]): 
            uri_candidate ([URIRef,str]): 
            highest_score ([int]): 

        Returns:
            Returns the uri and its highest score
        """

        query_found = None
        if type(value) is str:
            value = value.strip()
        if type(query) is str:
            query = query.strip()
        cosine_score = self.word_similarity_compare(str(value), str(query))
        if (cosine_score > sim_threshhold_content) and (cosine_score > highest_score):
            highest_score = cosine_score
            query_found = uri_candidate

        return query_found, highest_score

    def find_uri_for_query(self, query_instances, query, sim_threshhold):
        """ Given a list of tuples, tuples formed by <URIRef, dictionary>,
            returns the most suitable uri for a query.

        Args:
            query_instances (list(tuples(URIRef,dict))):  List of tuples.
            Those tuples are composed by the uri of the instances and all of its propertys
            gathered in a dictionary 

        Returns:
            Returns the most suitable uri for a query 
        """
        query_found = None
        instance_len = len(query_instances)
        i = 0
        dct_title = utils.get_uriref_str(DCTERMS.title)
        highest_score = 0
        while (not query_found) and (i < instance_len):
            (uri_candidate, metadata_candidate) = query_instances[i]
            posible_title_list = metadata_candidate.get(dct_title)
            if posible_title_list:
                for posible_title in posible_title_list:
                    query_found, highest_score = self.__auxiliary_find_best_option(
                        posible_title, query, uri_candidate, highest_score, sim_threshhold)

            i = i + 1
        return query_found

    def __auxiliary_find_best_option(self, value_i, query, uri_candidate, highest_score, sim_threshhold):
        """
        Helper function to find the best option for a given query and URI candidate.
        
        Args:
            value_i (int): The index of the value being evaluated.
            query (str): The query string.
            uri_candidate (str): The URI candidate string.
            highest_score (float): The current highest similarity score.
            sim_threshhold (float): The similarity threshold for considering a match.
        
        Returns:
            tuple: A tuple containing the query found and the highest score.
        """
        # Call the find_best_option() method to find the best option
        query_found, highest_score = self.find_best_option(
            value_i, query, uri_candidate, highest_score, sim_threshhold)
        
        # Return the query found and highest score
        return query_found, highest_score

