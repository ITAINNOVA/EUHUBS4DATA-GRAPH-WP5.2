
from end_point.logging_ita import application_logger
import nltk
from nltk.corpus import WordNetCorpusReader
from nltk.corpus import wordnet
import py3langid as langid
import en_core_web_md  # spacy
import es_core_news_md
# nltk.download('punkt')
# nltk.download("omw")
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# Tutorial: How to use wordnet in Spanish
# https://github.com/lingeringsocket/wn-mcr-transform

class SynsMaker():
    """ Class which uses wordnet API to return a list of synonyms
    for the words given as parameters to the function:
        extract_synonyms_from_word(self, processed_word, lang=None):
    This class only finds synonyms for Spanish and English words
    """

    def __init__(self, model_wordnet_path):
        try:
            application_logger.info("Let's check if wordnet is there")
            nltk.data.find('corpora/wordnet')
        except LookupError:
            application_logger.warning("No wordnet!")
            nltk.download('wordnet', download_dir='/root/nltk_data')
            application_logger.warning("No wordnet!")
        self.nlp_en = en_core_web_md.load()
        self.nlp_es = es_core_news_md.load()
        self.synonyms_wn = WordNetCorpusReader(model_wordnet_path, None)
        wordnet.ensure_loaded()
        self.synonyms_wn.ensure_loaded()

    def extract_synonyms_from_word(self, processed_word, lang=None):
        """
        Extracts synonyms from a processed word.
        
        Args:
            processed_word (str): The processed word.
            lang (str, optional): The language of the word. If not provided, it will be detected using langid.

        Returns:
            list: A list of synonyms for the word.
        """
        if not lang:
            lang, conf = langid.classify(processed_word)
        synonym_list = []
        if lang == 'es':
            if self.synonyms_wn and processed_word:
                synonym_list = self.get_synonyms_spanish(processed_word)
            else:
                application_logger.error("error")
        else:
            if processed_word:
                synonym_list = self.get_synonyms_english(processed_word)
            else:
                application_logger.error("error")

        return synonym_list

    def get_synonyms_spanish(self, word):
        """
        Get synonyms of a Spanish word using WordNet.

        Args:
            word (str): The word for which synonyms are to be retrieved.

        Returns:
            list: A list of synonyms for the given word.
        """
        return self.get_synonyms(word, self.synonyms_wn)

    def get_synonyms_english(self, word):
        """
        This function returns a list of synonyms for a given word in English.
        
        Args:
            word (str): The word to find synonyms for.
        
        Returns:
            list: A list of synonyms for the given word.
        """
        return self.get_synonyms(word, wordnet)

    def get_synonyms(self, word, word_net):
        """
        Get a list of synonyms from a word.
        :param word: The word.
        :return: A list of synonyms of the word.
        """
        synonyms = []
        for synset in word_net.synsets(word):
            for l in synset.lemmas():
                proccessed_lemma = l.name().replace('_', ' ')
                if not proccessed_lemma in synonyms:
                    synonyms.append(proccessed_lemma)
        return synonyms

    def semantic_spanish_score(self, sentence1, sentence2):
        """
        Calculate the semantic score between two Spanish sentences.

        Args:
            sentence1 (str): The first sentence.
            sentence2 (str): The second sentence.

        Returns:
            float: The semantic score between the two sentences.
        """

        # Calculate the semantic score between sentence1 and sentence2
        score1 = self.semantic_score(sentence1, sentence2, self.synonyms_wn, self.nlp_es)

        # Calculate the semantic score between sentence2 and sentence1
        score2 = self.semantic_score(sentence2, sentence1, self.synonyms_wn, self.nlp_es)

        # Calculate the average of the two semantic scores
        average_score = (score1 + score2) / 2

        return average_score

    def semantic_english_score(self, sentence1, sentence2):
        """
        Calculate the semantic English score between two sentences.

        Args:
            sentence1 (str): The first sentence.
            sentence2 (str): The second sentence.

        Returns:
            float: The semantic English score.

        """
        # Calculate the semantic score between sentence1 and sentence2
        score1 = self.semantic_score(sentence1, sentence2, wordnet, self.nlp_en)
        
        # Calculate the semantic score between sentence2 and sentence1
        score2 = self.semantic_score(sentence2, sentence1, wordnet, self.nlp_en)
        
        # Calculate the average of the two scores
        average_score = (score1 + score2) / 2
        
        return average_score

    def semantic_score(self, sentence1_input, sentence2_input, word_net, nlp):
        """
        Purpose: Computes sentence similarity using Wordnet path_similarity().
        Input: Synset lists representing sentence 1 and sentence 2.
        Output: Similarity score as a float

        """
        sumSimilarityscores = 0
        scoreCount = 0
        avgScores = 0
        doc2 = list()
        doc1 = list()
        synset1 = list()
        synset2 = list()
        # For each synset in the first sentence...
        sentence1 = sentence1_input.split(" ")
        sentence2 = sentence2_input.split(" ")
        for word1 in sentence1:

            if not word1:
                continue
            word1 = word1.strip().replace(r"[^A-Za-z0-9]", "").lower()
            synsetScore = 0
            similarityScores = []
            synset1 = word_net.synsets(word1)
            doc1 = nlp(word1)
            # For each synset in the second sentence...
            for word2 in sentence2:
                try:
                    if not word2:
                        continue
                    word2 = word2.strip().replace(r"[^A-Za-z0-9]", "").lower()
                    synset2 = word_net.synsets(word2)
                    doc2 = nlp(word2)
                    # Only compare synsets with the same POS tag. Word to word knowledge
                    # measures cannot be applied across different POS tags.
                    if len(synset1) > 0 and len(synset2) > 0 and len(doc1) > 0 and len(doc2) > 0:
                        if doc1[0].pos_ == doc2[0].pos_:
                            # Note below is the call to path_similarity mentioned above.
                            synsetScore = synset1[0].path_similarity(
                                synset2[0])
                            if synsetScore != None:
                                similarityScores.append(synsetScore)
                        # If there are no similarity results but the SAME WORD is being
                            # compared then it gives a max score of 1.
                            elif word1 == word2:
                                synsetScore = 1
                                similarityScores.append(synsetScore)
                        else:
                            if word1 == word2:
                                synsetScore = 1
                                similarityScores.append(synsetScore)
                    else:
                        if word1 == word2:
                            synsetScore = 1
                            similarityScores.append(synsetScore)
                except Exception as e:
                    application_logger.error(e, exc_info=True)
                    application_logger.error(
                        f"{str(e)} - {word1} - {word2} - {str(len(doc1))} - {str(len(doc2))} - {str(len(synset1))} - {str(len(synset2))} ")
            if (len(similarityScores) > 0):
                sumSimilarityscores += max(similarityScores)
                scoreCount += 1
        # Average the summed, maximum similarity scored and return.
        if scoreCount > 0:
            avgScores = sumSimilarityscores / scoreCount
        return (avgScores)
