from random import Random
from simiir.serp_impressions.base_serp_impression import BaseSERPImpression

class StochasticSERPImpression(BaseSERPImpression):
    """
    An implementation of the SERP impression component that is stochastic.
    Works out the judged precision. If the precision is less than a certain threshold,
    we roll the dice (bad_abandon_probability) -- and if it is above, we also roll the
    dice (good_abandon_probability).
    """
    def __init__(self,
                 search_context,
                 qrel_file,
                 host=None,
                 port=None,
                 good_abandon_probability=0.5,
                 bad_abandon_probability=0.5,
                 base_seed=0,
                 viewport_precision_threshold=0.1):
        super(StochasticSERPImpression, self).__init__(search_context=search_context,
                                                       qrel_file=qrel_file,
                                                       host=host,
                                                       port=port)
        
        self.__good_abandon_probability = good_abandon_probability
        self.__bad_abandon_probability = bad_abandon_probability
        self.__viewport_precision_threshold = viewport_precision_threshold
        
        self.__random = Random()
        self.__random.seed(base_seed + 0)
    
    
    def is_serp_attractive(self):
        """
        Determines whether the SERP is sufficiently attractive enough to enter.
        Uses judgements from the TREC QRELS to work out the patch type and judgement of snippets in the viewport.
        But a stochastic element is introduced to determine if the simulated user enters the patch or not.
        """
        # Work out the patch type first, using code from the base (SimpleSERPImpression) class.
        judgements = self._get_patch_judgements()
        patch_type = self._calculate_patch_type(judgements)
        self._set_query_patch_type(patch_type)
        
        # Now work out whether we enter the SERP or not.
        # Again, we use the TREC QREL judgements here (is that correct, should this be rolled, too? So confusing.).
        judged_precision = sum(judgements) / float(len(judgements))
        die_roll = self.__random.random()
        
        # Work out whether the SERP should be considered attractive or not here.
        threshold = self.__bad_abandon_probability
        
        if judged_precision > self.__viewport_precision_threshold:
            threshold = self.__good_abandon_probability
        
        if die_roll < threshold:
            return False
        
        return True
        
        # # Old code
        # if judged_precision < self.__viewport_precision_threshold:
        #     # Precision is less than the threshold, so we assume the SERP is of poor quality.
        #
        #     if die_roll <= self.__bad_abandon_probability:
        #         return False
        #     else:
        #         return True
        #
        # # If we get here, the precision is at or greater than the threshold, so we assume the SERP is "good".
        # if die_roll <= self.__good_abandon_probabilty:
        #     return False
        #
        # return True