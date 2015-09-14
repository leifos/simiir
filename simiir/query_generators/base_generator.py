import abc
from whoosh.lang.porter import stem
from ifind.common.query_ranker import QueryRanker
from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration, BiTermQueryGeneration, TriTermQueryGeneration
from ifind.common.smoothed_language_model import BayesLanguageModel
import logging

log = logging.getLogger('query_generators.base_generator')

#TODO(leifos): queries are not being recorded in all classes, we need a solution that logs all queries in all classes
# without having to add something like: self._log_queries(interleaved_queries)

class BaseQueryGenerator(object):
    """
    The base query generator class. Although you can use this query generator directly at present, refactoring is required to abstract the inner workings of the query generators more.
    """
    def __init__(self, output_controller, stopword_file, background_file=[], topic_model=0):  # TODO(dmax): stopwords_file to be a list!
        self._stopword_file = stopword_file
        self._background_file = background_file
        self._topic_model = topic_model
        self._output_controller = output_controller
    
    def _generate_topic_language_model(self, topic):

        topic_model_switch = {0: self._generate_naive_topic_language_model,
                              1: self._generate_title_topic_language_model}

        if self._topic_model in topic_model_switch:
            return topic_model_switch[self._topic_model](topic)
        else:
            return self._generate_naive_topic_language_model(topic)
            
    def _generate_naive_topic_language_model(self, topic):
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
        
    def _generate_title_topic_language_model(self, topic):
        """
        Generates a language model based on the content from the title and description of the TREC title/description.
        """
        topic_text = topic.title
        topic_background = topic.content

        document_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        document_extractor.extract_queries_from_text(topic_text)
        document_term_counts = document_extractor.query_count

        document_extractor.extract_queries_from_text(topic_background)

        background_term_counts = document_extractor.query_count

        title_language_model = LanguageModel(term_dict=document_term_counts)
        background_language_model = LanguageModel(term_dict=background_term_counts)
        topic_language_model = BayesLanguageModel(title_language_model, background_language_model, beta=10)
        return topic_language_model


    def generate_query_list(self, topic):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """
        topic_text = topic.content
        topic_lang_model = self._generate_topic_language_model(topic)
        
        bi_query_generator = BiTermQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        tri_query_generator = TriTermQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        
        tri_query_list = tri_query_generator.extract_queries_from_text(topic_text)
        bi_query_list = bi_query_generator.extract_queries_from_text(topic_text)
        
        query_list = tri_query_list + bi_query_list
        
        query_ranker = QueryRanker(smoothed_language_model=topic_lang_model)
        query_ranker.calculate_query_list_probabilities(query_list)
        return query_ranker.get_top_queries(100)



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
    
    def _log_queries(self, queries):
        """
        Given a log of queries, adds each one to the log file for the running simulation.
        For informational purposes, really.
        """
        count = 1
        
        for query in queries:
            log.debug( query )
            self._output_controller.log_query("{0} {1}".format(count, query[0]))
            count = count + 1