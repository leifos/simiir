from random import random
from simiir.text_classifiers.base_classifier import BaseTextClassifier

class RankBiasedTextClassifier(BaseTextClassifier):
    """
    Implements the basic Rank-Biased Precision (RBP) metric, as per Moffat and Zobel (2008).
    The probability of considering an item relevant gradually decreases as the depth increases.
    A patience factor also considers the rate at which the decrease occurs.
    """
    def __init__(self, topic, search_context, patience=0.5):
        """
        
        """
        super(RankBiasedTextClassifier, self).__init__(topic, search_context)
        self.__patience = patience
        
    def is_relevant(self, document):
        """
        Calculates the RBP score at a given rank (with the patience factor considered), and returns True/False after a die roll.
        """
        serp_depth = self._search_context.get_current_serp_position()
        rbp_score = (1.0/serp_depth)**(1-self.__patience)
        dp = random()
        
        if dp > rbp_score:
            return True
        else:
            return False
        
    # Old is_relevant(). This wasn't quite right; this examined prior judgements, too.
    
    # trec_judgement = self._get_judgment(self._topic.id, document.doc_id)
    # snippets = self._search_context.get_examined_snippets()
    #
    # trec_judgements = []
    #
    # for snippet in snippets:
    #     judgement = self._get_judgment(self._topic.id, snippet.doc_id)
    #
    #     # RBP requires binary relevance judgements (e.g. 0 for nonrelevant, 1 for relevant.)
    #     # Remove any graded relevance judgement (i.e. anything above 0 is simply considered 'relevant').
    #     if judgement > 0:
    #         judgement = 1
    #
    #     trec_judgements.append(judgement)
    #
    # # Calculate the RBP score for the latest snippet, considering all TREC judgements up to this point.
    # rbp_score = self.__calculate_rbp_score(trec_judgements)
    # dp = random()
    #
    # if dp > rbp_score:
    #     return True
    # else:
    #     return False
    
    # def __calculate_rbp_score(self, judgements):
    #     """
    #     Rank-biased precision, as per Moffat and Zobel (2008).
    #     Assumes that the RBP score for the last value in the judgements list is wanted, therefore depth==len(judgements).
    #     This is incorrect; keeping for reference. This is more akin to INST.
    #     """
    #     summed = 0
    #     depth = len(judgements)
    #
    #     for i in range(0, depth):
    #         summed = summed + judgements[i] * (float(self.__patience)**(i))  # Raised to the power of i because of the zero-based value for i.
    #
    #     return (1-self.__patience) * summed