import abc
from random import Random
from simiir.search_interfaces import Document
from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from simiir.serp_impressions import PatchTypes, SERPImpression
from simiir.serp_impressions.base_serp_impression import BaseSERPImpression
from simiir.utils.data_handlers import InformedFileDataHandler, InformedRedisDataHandler

class StochasticSERPImpression(BaseSERPImpression):
    """
    A stochastic-based approach to determining whether a SERP should be examined in more detail or not.
    Uses a roll of a dice next to a probability to determine whether the SERP is entered.
    For determining the patch type, seeded judgements are used (as per text classifiers).
    Patch type does not affect the SERP judgement, so this should be okay to use.
    """
    def __init__(self, search_context, topic, viewport_size=10, good_abandon_probability=0.5, bad_abandon_probability=0.5, patch_type_threshold=0.4, qrel_file=None, base_seed=0, host=None, port=0):
        super(StochasticSERPImpression, self).__init__(search_context, topic, patch_type_threshold=patch_type_threshold)
        self.__viewport_size = viewport_size
        self.__good_abandon_probability = good_abandon_probability
        self.__bad_abandon_probability = bad_abandon_probability
        
        self._host = host
        self._port = port
        self._filename = qrel_file
        
        if self._host is not None:
            self.data_handler = 1  # Given a hostname; assume that a Redis cache will be used.
        else:
            self.data_handler = 0  # Sets the data handler to 0 by default (file-based). Can also set to 1 (Redis-based).
        
        self.__random = Random()
        self.__random.seed(base_seed + 0)  # Just use base_seed for the seed value
    
    def initialise(self):
        """
        No prior initialisations are required.
        """
        pass
    
    @property
    def data_handler(self):
        """
        Setter for the relevance revision technique.
        """
        if not hasattr(self, '_data_handler'):
            self._data_handler = 0

        return self._data_handler
    
    @data_handler.setter
    def data_handler(self, value):
        """
        The getter for the relevance revision technique.
        Given one of the key values in rr_strategies below, instantiates the relevant approach.
        """
        dh_strategies = {
            0: InformedFileDataHandler,
            1: InformedRedisDataHandler
        }
        
        if value not in dh_strategies.keys():
            raise ValueError("Value {0} for the data handler approach is not valid.".format(value))
        
        self._data_handler = dh_strategies[value](self._filename, host=self._host, port=self._port)
    
    def _get_handler_judgement(self, topic_id, doc_id):
        """
        Helper function that returns the judgement of the document
        If the value does not exist in the qrels, it checks topic '0' - a non-existant topic, which you can put pre-rolled relevance values
        The default value returned is 0, indicated no gain/non-relevant.

        topic_id (string): the TREC topic number
        doc_id (srting): the TREC document number
        """
        val = self._data_handler.get_value(topic_id, doc_id)  # Does the document exist?
                                                              # Pulls the answer from the data handler.
        
        if not val:  # If not, we fall back to the generic topic.
            val = self._data_handler.get_value('0', doc_id)
        if not val:  # if still no val, assume the document is not relevant.
            val = 0
        
        return val
    
    def get_impression(self):
        """
        Simplistic approach; always assume that the SERP has some degree of relevancy, thus the searcher enters the SERP to judge snippets.
        """
        judgements = self.__get_patch_judgements()
        patch_type = self._calculate_patch_type(judgements)
        
        # Judgement of SERP is proportional to the finding of one item in the viewable area.
        one_rel = 1.0 / len(judgements)
        avg = sum(judgements) / float(len(judgements))
        die_roll = self.__random.random()
        
        # If it's a poor SERP... roll the dice and abandon if everything checks out.
        if avg <= one_rel:
            
            if die_roll <= self.__bad_abandon_probability:
                return SERPImpression(False, patch_type)
            else:
                return SERPImpression(True, patch_type)
        
        # If we get here, the patch is considered "good"
        if die_roll <= self.__good_abandon_probability:
            return SERPImpression(False, patch_type)
        
        return SERPImpression(True, patch_type)
    
    def __get_patch_judgements(self):
        """
        Gets the patch judgements from the TREC QREL file.
        """
        results_len = self._search_context.get_current_results_length()
        results_list = self._search_context.get_current_results()
        goto_depth = self.__viewport_size
        
        if results_len < goto_depth:
            goto_depth = results_len
        
        judgements = []
        
        for i in range(0, goto_depth):
            snippet = Document(results_list[i].whooshid, results_list[i].title, results_list[i].summary, results_list[i].docid)
            judgement = self.__get_judgement(results_list[i].docid)
            judgements.append(judgement)
            
        return judgements
    
    def __get_judgement(self, doc_id):
        """
        Gets the judgement for the given document (and topic, defined in BaseSERPImpression).
        If the document doesn't exist, then we try the fallback topic; else we return 0.
        """
        val = self._get_handler_judgement(self._topic.id, doc_id)  # Does the document exist?
        
        if not val:  # If not, we fall back to the generic topic.
            val = self._get_handler_judgement('0', doc_id)
        if not val:  # if still no val, assume the document is not relevant.
            val = 0
        
        if val > 0:
            val = 1  # Binary judgements (for now)
        
        return val