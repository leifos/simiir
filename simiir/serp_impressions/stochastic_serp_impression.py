import random
from simiir.search_interfaces import Document
from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from simiir.serp_impressions import PatchTypes, SERPImpression
from simiir.serp_impressions.base_serp_impression import BaseSERPImpression

class StochasticSERPImpression(BaseSERPImpression):
    """
    A stochastic-based approach to determining whether a SERP should be examined in more detail or not.
    Uses a roll of a dice next to a probability to determine whether the SERP is entered.
    For determining the patch type, seeded judgements are used (as per text classifiers).
    Patch type does not affect the SERP judgement, so this should be okay to use.
    """
    def __init__(self, search_context, topic, viewport_size=10, abandon_probability=0.5, patch_type_threshold=0.4, qrel_file=None):
        super(StochasticSERPImpression, self).__init__(search_context, topic, patch_type_threshold=patch_type_threshold)
        self.__viewport_size = viewport_size
        self.__abandon_probability = abandon_probability
        self.__qrel_handler = TrecQrelHandler(qrel_file)
    
    def initialise(self):
        """
        No prior initialisations are required.
        """
        pass
    
    def get_impression(self):
        """
        Simplistic approach; always assume that the SERP has some degree of relevancy, thus the searcher enters the SERP to judge snippets.
        """
        die_roll = random.random()
        
        if die_roll > self.__abandon_probability:
            examine = True
        else:
            examine = False
        
        judgements = self.__get_patch_judgements()
        patch_type = self._calculate_patch_type(judgements)
        
        return SERPImpression(examine, patch_type)
    
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
        val = self.__qrel_handler.get_value_if_exists(self._topic.id, doc_id)  # Does the document exist?
        
        if not val:  # If not, we fall back to the generic topic.
            val = self.__qrel_handler.get_value_if_exists('0', doc_id)
        if not val:  # if still no val, assume the document is not relevant.
            val = 0
        
        if val > 0:
            val = 1  # Binary judgements (for now)
        
        return val