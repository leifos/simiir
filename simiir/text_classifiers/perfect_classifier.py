from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from simiir.text_classifiers.stochastic_informed_trec_classifier import StochasticInformedTrecTextClassifier

class PerfectTrecTextClassifier(StochasticInformedTrecTextClassifier):
    """
    A simple text classifier that only judges items as relevant if they are actually TREC relevant.
    """
    def __init__(self, topic, search_context, qrel_file, host=None, port=0):
        super(StochasticInformedTrecTextClassifier, self).__init__(topic, search_context, qrel_file, host=None, port=0)
    
    def is_relevant(self, document):
        """
        Returns true if the item is TREC relevant (where the judgement is >= 1); False otherwise.
        """
        val = self._get_judgment(self._topic.id, document.doc_id)
        
        if val > 0:
            return True
        
        return False