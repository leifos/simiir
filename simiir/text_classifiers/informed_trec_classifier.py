__author__ = 'leif'

from text_classifiers.base_informed_trec_classifier import BaseInformedTrecTextClassifier
from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from random import random

class InformedTrecTextClassifier(BaseInformedTrecTextClassifier):
    """
    A concrete implementation of BaseInformedTrecTextClassifier.
    Loads QRELS from disk.
    """
    def __init__(self, topic, qrel_file, stopword_file=[], background_file=[], rprob=1.0, nprob=1.0):
        """

        """
        super(InformedTrecTextClassifier, self).__init__(topic, qrel_file, stopword_file, background_file, rprob=rprob, nprob=nprob)
        
    
    def _initialise_handler(self, qrel_file):
        """
        This is spun off from the constructor to make way for the Redis classifier.
        Contrete implementation of the base class!
        """
        self._trecqrels = TrecQrelHandler(qrel_file)  # Easy!