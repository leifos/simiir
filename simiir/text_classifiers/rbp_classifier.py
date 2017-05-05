import abc
from random import random
from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from simiir.text_classifiers.base_informed_trec_classifier import BaseInformedTrecTextClassifier

class RankBiasedInformedTrecTextClassifier(BaseInformedTrecTextClassifier):
    """
    Takes the TREC QREL file, and the probabilities rprob and nprob
    if a document is TREC relevant, then the probability that it is judged relevant is given by rprob
    if it is NOT TREC releavnt, then the probabiltiy that iit is judged non-relevant is given by nprob

    rprob and nprob are set to 1.0 by default, so that the classifier is deterministic,
    i.e. it returns the exact TREC relevance judgement
    """
    def __init__(self, topic, search_context, qrel_file, patience=0.5):
        """
        
        """
        super(RankBiasedInformedTrecTextClassifier, self).__init__(topic, search_context, qrel_file)
        self.__patience = patience
        
    @abc.abstractmethod
    def is_relevant(self, document):
        """
        Rolls the dice, and decides whether a relevant document stays relevant or not (and similarly for a non-relevant).
        """
        trec_judgement = self._get_judgment(self._topic.id, document.doc_id)
        snippets = self._search_context.get_examined_snippets()
        
        trec_judgements = []
        
        for snippet in snippets:
            judgement = self._get_judgment(self._topic.id, snippet.doc_id)
            
            # RBP requires binary relevance judgements (e.g. 0 for nonrelevant, 1 for relevant.)
            # Remove any graded relevance judgement (i.e. anything above 0 is simply considered 'relevant').
            if judgement > 0:
                judgement = 1
            
            trec_judgements.append(judgement)
        
        # Calculate the RBP score for the latest snippet, considering all TREC judgements up to this point.
        rbp_score = self.__calculate_rbp_score(trec_judgements)
        dp = random()
        
        if dp > rbp_score:
            return True
        else:
            return False
    
    def __calculate_rbp_score(self, judgements):
        """
        Rank-biased precision, as per Moffat and Zobel (2008).
        Assumes that the RBP score for the last value in the judgements list is wanted, therefore depth==len(judgements).
        """
        summed = 0
        depth = len(judgements)
        
        for i in range(0, depth):
            summed = summed + judgements[i] * (float(self.__patience)**(i))  # Raised to the power of i because of the zero-based value for i.
        
        return (1-self.__patience) * summed