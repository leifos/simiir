__author__ = 'leif'


import abc
from simiir.text_classifiers.base_informed_trec_classifier import BaseInformedTrecTextClassifier
from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from random import random

class StochasticInformedTrecTextClassifier(BaseInformedTrecTextClassifier):
    """
    Takes the TREC QREL file, and the probabilities rprob and nprob
    if a document is TREC relevant, then the probability that it is judged relevant is given by rprob
    if it is NOT TREC releavnt, then the probabiltiy that iit is judged non-relevant is given by nprob

    rprob and nprob are set to 1.0 by default, so that the classifier is deterministic,
    i.e. it returns the exact TREC relevance judgement
    """
    def __init__(self, topic, qrel_file, rprob=1.0, nprob=1.0):
        """

        """
        super(BaseInformedTrecTextClassifier, self).__init__(topic, stopword_file=[], background_file=[])
        self._initialise_handler(qrel_file)

        self._rel_prob = rprob
        self._nrel_prob = nprob

    @abc.abstractmethod
    def is_relevant(self, document):
        """
        Rolls the dice, and decides whether a relevant document stays relevant or not (and similarly for a non-relevant)
        """
        val = self._get_judgement(self._topic.id, document.doc_id)


        dp = random()

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