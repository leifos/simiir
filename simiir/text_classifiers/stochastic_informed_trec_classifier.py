__author__ = 'leif'


import abc
from random import Random
from simiir.text_classifiers.base_informed_trec_classifier import BaseInformedTrecTextClassifier
from ifind.seeker.trec_qrel_handler import TrecQrelHandler

class StochasticInformedTrecTextClassifier(BaseInformedTrecTextClassifier):
    """
    Takes the TREC QREL file, and the probabilities rprob and nprob
    if a document is TREC relevant, then the probability that it is clicked/judged relevant is given by rprob
    if it is NOT TREC releavnt, then the probabiltiy that iit is clicked/judged non-relevant is given by nprob

    rprob and nprob are set to 1.0 by default, so that the classifier is deterministic,
    i.e. it always clicks or judges relevant
    """
    def __init__(self, topic, search_context, qrel_file, rprob=1.0, nprob=1.0, base_seed=0, host=None, port=0):
        """

        """
        super(StochasticInformedTrecTextClassifier, self).__init__(topic, search_context, qrel_file, host=host, port=port)
        
        self._rel_prob = rprob
        self._nrel_prob = nprob

        
        self.__random = Random()
        self.__random.seed(base_seed + 256)

    @abc.abstractmethod
    def is_relevant(self, document):
        """
        Rolls the dice, and decides whether a relevant document stays relevant or not (and similarly for a non-relevant).
        """
        val = self._get_judgment(self._topic.id, document.doc_id)
        dp = self.__random.random()


        #print(self._rel_prob, self._nrel_prob, dp, val)
        
        # Updated by Leif in September 2017.

        threshold = self._nrel_prob
        if val > 0:
            threshold = self._rel_prob

        if dp > threshold:
            return False
        else:
            return True

        """
        # old code
        if val > 0: # if the judgement is relevant

            if dp > self._rel_prob:

                return False
            else:
                return True
        else:
            if dp > self._nrel_prob:
                return True
            else:
                return False

        """