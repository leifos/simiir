import abc
from whoosh.lang.porter import stem
from ifind.common.query_ranker import QueryRanker
from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration, BiTermQueryGeneration, TriTermQueryGeneration
from ifind.common.smoothed_language_model import BayesLanguageModel
import logging

log = logging.getLogger('query_generators.base_generator')

class BaseQueryGenerator(object):
    """
    The base query generator class.
    Generates 2-word queries from the topic title and description (content)
    ranked by the likelihood of producing that query given the topic.

    You can use this to inherit from to make your own query generator
    """
    def __init__(self, stopword_file, background_file=[]):
        self._stopword_file = stopword_file
        self._background_file = background_file

    def _generate_topic_language_model(self, topic, search_context=None):

        """
        Given a Topic object, returns a language model representation for the given topic.
        Override this method in inheriting classes to generate and return different language models.
        """
        topic_text = "{0} {1}".format(topic.title, topic.content)

        document_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        document_extractor.extract_queries_from_text(topic_text)
        document_term_counts = document_extractor.query_count

        # The langauge model we return is simply a representtaion of the number of times terms occur within the topic text.
        topic_language_model = LanguageModel(term_dict=document_term_counts)
        return topic_language_model


    def generate_query_list(self, topic, search_context=None):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """
        topic_text = "{0} {1}".format(topic.title, topic.content)

        topic_lang_model = self._generate_topic_language_model(topic, search_context)
        
        bi_query_generator = BiTermQueryGeneration(minlen=3, stopwordfile=self._stopword_file)

        bi_query_list = bi_query_generator.extract_queries_from_text(topic_text)

        query_list = bi_query_list
        
        query_ranker = QueryRanker(smoothed_language_model=topic_lang_model)
        query_ranker.calculate_query_list_probabilities(query_list)
        gen_query_list = query_ranker.get_top_queries(100)

        return gen_query_list


    @abc.abstractmethod
    def _rank_terms(self, terms, **kwargs):
        """
        Given a list of query terms (list of strings) as parameter terms, returns a list of those queries - ranked in some way.
        Additional parameters may be passed (if required for a given implementation) through kwargs.
        """
        pass
    
    def _stem_term(self, term):
        """
        Applies the Porter stemming algorithm (implementation from the Whoosh IR toolkit) to a given term, term.
        The returned string represents the stemmed version of the term.
        """
        return stem(term)
    

