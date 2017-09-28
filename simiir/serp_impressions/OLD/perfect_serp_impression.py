import abc
from simiir.search_interfaces import Document
from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from simiir.serp_impressions import PatchTypes, SERPImpression
from simiir.serp_impressions.base_serp_impression import BaseSERPImpression
from simiir.utils.data_handlers import get_data_handler

class PerfectSERPImpression(BaseSERPImpression):
    """
    A simple approach to SERP impression judging.
    The de facto approach used in prior simulations; assume it's worth examining. Always return True.
    """
    def __init__(self, search_context, topic, qrel_file, viewport_size=10, patch_type_threshold=0.4, host=None, port=0):
        super(PerfectSERPImpression, self).__init__(search_context, topic, patch_type_threshold=patch_type_threshold)
        self._host = host
        self._port = port
        self._filename = qrel_file
        self.__viewport_size = viewport_size
        
        self._data_handler = get_data_handler(filename=self._filename, host=self._host, port=self._port, key_prefix='serp')
    
    def initialise(self):
        """
        No prior initialisations are required.
        """
        pass
    
    def get_impression(self):
        """
        Simplistic approach; always assume that the SERP has some degree of relevancy, thus the searcher enters the SERP to judge snippets.
        """
        results_len = self._search_context.get_current_results_length()
        results_list = self._search_context.get_current_results()
        
        goto_depth = self.__viewport_size
        
        if results_len < goto_depth:
            goto_depth = results_len
        
        judgements = []
        
        for i in range(0, goto_depth):
            snippet = Document(results_list[i].whooshid, results_list[i].title, results_list[i].summary, results_list[i].docid)
            trec_judgement = self._data_handler.get_value_fallback(self._topic.id, results_list[i].docid)
            
            if trec_judgement is None:
                trec_judgement = 0  # Assume for unjudged documents that it is not relevant.
            elif trec_judgement > 0:
                trec_judgement = 1
            
            judgements.append(trec_judgement)
        
        patch_type = self._calculate_patch_type(judgements)
        
        # Judgement of SERP is proportional to the finding of one item in the viewable area.
        one_rel = 1.0 / len(judgements)
        avg = sum(judgements) / float(len(judgements))
        
        if avg <= one_rel:
            return SERPImpression(False, patch_type)
        
        return SERPImpression(True, patch_type)