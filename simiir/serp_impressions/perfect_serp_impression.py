from simiir.search_interfaces import Document
from simiir.serp_impressions.base_serp_impression import BaseSERPImpression

class PerfectSERPImpression(BaseSERPImpression):
    """
    
    """
    def __init__(self,
                 search_context,
                 topic,
                 qrel_file,
                 host=None,
                 port=None,
                 dcg_discount=0.5,
                 patch_type_threshold=0.6,
                 viewport_size=10,
                 viewport_precision_threshold=0.1):
        super(PerfectSERPImpression, self).__init__(search_context=search_context,
                                                       topic=topic,
                                                       qrel_file=qrel_file,
                                                       host=host,
                                                       port=port,
                                                       dcg_discount=dcg_discount,
                                                       patch_type_threshold=patch_type_threshold,
                                                       viewport_size=viewport_size)
        
        self.__viewport_precision_threshold = viewport_precision_threshold
    
    
    def is_serp_attractive(self):
        """
        Determines whether the SERP is sufficiently attractive enough to enter.
        Uses "perfect judgements", that is, judgements from the TREC QRELS.
        """
        # Work out the patch type first, using code from the base (SimpleSERPImpression) class.
        judgements = self._get_patch_judgements()
        patch_type = self._calculate_patch_type(judgements)
        self._set_query_patch_type(patch_type)
        
        results_len = self._search_context.get_current_results_length()
        results_list = self._search_context.get_current_results()
        goto_depth = self._viewport_size
        
        if results_len < goto_depth:  # Sanity check -- what if the SERP returned is super small?
            goto_depth = results_len
        
        judged_precision = sum(judgements) / float(len(judgements))
        
        if judged_precision < self.__viewport_precision_threshold:
            # We have a poor quality SERP.
            return False
        
        # If we get here, the SERP will be of quality good enough to enter.
        return True