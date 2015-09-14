__author__ = 'david'

import abc
from text_classifiers.base_classifier import BaseTextClassifier
from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from random import random

class BaseInformedTrecTextClassifier(BaseTextClassifier):
    """
    Takes the TREC QREL file, and the probabilities rprob and nprob
    if a document is TREC relevant, then the probability that it is judged relevant is given by rprob
    if it is NOT TREC releavnt, then the probabiltiy that iit is judged non-relevant is given by nprob

    rprob and nprob are set to 1.0 by default, so that the classifier is deterministic,
    i.e. it returns the exact TREC relevance judgement
    """
    def __init__(self, topic, qrel_file, stopword_file=[], background_file=[], rprob=1.0, nprob=1.0):
        """

        """
        super(BaseInformedTrecTextClassifier, self).__init__(topic, stopword_file, background_file)
        self._initialise_handler(qrel_file)
        
        self._rel_prob = rprob
        self._nrel_prob = nprob
    
    
    @abc.abstractmethod
    def _initialise_handler(self, qrel_file):
        """
        This is spun off from the constructor to make way for the Redis classifier.
        """
        pass


    def make_topic_language_model(self):
        """

        """
        print "No Topic model required for Trec Classifier"

    def is_relevant(self, document):
        """

        """
        val = self._trecqrels.get_value_if_exists(self._topic.id, document.doc_id)  # Does the document exist?
        
        if not val:  # If not, we fall back to the generic topic.
            val = self._trecqrels.get_value('0', document.doc_id)
        
        dp = random()
        
        if val > 0:
            if dp > self._rel_prob:
                return False
            else:
                return True
        else:
            if dp > self._nrel_prob:
                return True
            else:
                return False