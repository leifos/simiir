import abc
from whoosh.lang.porter import stem
from simiir.utils import lm_methods
from ifind.search.query import Query
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
    def __init__(self, stopword_file, background_file=None, allow_similar=False):
        self._stopword_file = stopword_file
        self._background_file = background_file
        self.updating = False
        self.update_method = 1
        self._query_list = None
        self.background_language_model = None
        self.__allow_similar = allow_similar
        
        if self._background_file:
            self.background_language_model = lm_methods.read_in_background(self._background_file)

    def _generate_topic_language_model(self, search_context):

        """
        Given a Topic object, returns a language model representation for the given topic.
        Override this method in inheriting classes to generate and return different language models.
        """
        topic = search_context.topic
        topic_text = "{0} {1}".format(topic.title, topic.content)

        document_term_counts = lm_methods.extract_term_dict_from_text(topic_text, self._stopword_file)

        # The language model we return is simply a representation of the number of times terms occur within the topic text.
        topic_language_model = LanguageModel(term_dict=document_term_counts)
        return topic_language_model


    def generate_query_list(self, search_context):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """
        topic = search_context.topic
        topic_text = "{0} {1}".format(topic.title, topic.content)

        topic_lang_model = self._generate_topic_language_model(search_context)
        
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
    

    def update_model(self, search_context):
        """
        Enables the model of query/topic to be updated, based on the search context
        The update model based on the documents etc in the search context (i.e. memory of the user)

        :param  search_context: search_contexts.search_context object
        :return: returns True is topic model is updated.
        """
        return False


    def get_next_query(self, search_context):
        """
        Returns the next query - if one that hasn't been issued before is present.
        """
        if self._query_list is None:
            self._query_list = self.generate_query_list(search_context)
        
        if search_context.query_limit > 0:  # If query_limit is a positive integer, a query limit is enforced. So check the length.
            number_queries = len(search_context.get_issued_queries())
            
            if number_queries == search_context.query_limit:  # If this condition is met, no more queries may be issued.
                return None
        
        issued_query_list = search_context.get_issued_queries()
        
        for query in self._query_list:
            candidate_query = query[0]
            
            # Allow similar queries to be issued (perhaps for mirroring real-world users)
            if self.__allow_similar and not self._has_query_been_issued(issued_query_list, candidate_query):
                return candidate_query
            
            # Otherwise, we are generating queries synthetically so we disallow this.
            if not self._has_query_been_issued(issued_query_list, candidate_query):
                if not self._had_similar_query_been_issued(issued_query_list, candidate_query):
                    return candidate_query  # This query has not been issued before, so say it's the next one to issue!

        return None
    
    def _has_query_been_issued(self, issued_query_list, query_candidate):
        """
        By examining previously examined queries in the search session, returns a boolean indicating whether
        the query terms provided have been previously examined. True iif they have, False otherwise.
        :param: issued_query_list is a list of  ifind.search.query objects
        :param query_candidate: string of query terms
        """
        query_candidate_object = Query(query_candidate)  # Strip punctutation, etc - so we compare like-for-like!
        query_candidate_processed = query_candidate_object.terms
        
        for query in issued_query_list:
            query_str = query.terms

            if query_candidate_processed == query_str:
                return True

        return False


    def _had_similar_query_been_issued(self, issued_query_list, query_candidate):
        """
        :param: issued_query_list is a list of  ifind.search.query objects
        :param query_candidate: string of query terms
        :return: True, if a similar query has been already issued, else False
        If all the terms exist in a previous queries, then it is similar.

        """

        candidate_terms = query_candidate.split()
        n = len(candidate_terms)


        for query in issued_query_list:
            query_str = query.terms

            i = 0
            for terms in candidate_terms:

                if query_str.find(terms)>=0:
                    i += 1

            if i == n:
                return True

        return False