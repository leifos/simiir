__author__ = 'david'

import abc
from simiir.text_classifiers.base_classifier import BaseTextClassifier
from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from random import random

class BaseInformedTrecTextClassifier(BaseTextClassifier):
    """
    Takes the TREC QREL file and loads it into a TrecQrelHandler

    Abstract method is_relevant() needs to be implemented.
    """
    def __init__(self, topic, qrel_file):
        """

        """
        super(BaseInformedTrecTextClassifier, self).__init__(topic, stopword_file=[], background_file=[])
        self._initialise_handler(qrel_file)
        
        #self._rel_prob = rprob
        #self._nrel_prob = nprob
    

    def _initialise_handler(self, qrel_file):
        """
        This is spun off from the constructor to make way for the Redis classifier.
        """

        self._trecqrels = TrecQrelHandler(qrel_file)

    def make_topic_language_model(self):
        """

        """
        print "No Topic model required for Trec Classifier"



    def _get_judgement(self, topic_id, doc_id):
        """
        Helper function that returns the judgement of the document
        If the value does not exist in the qrels, it checks topic '0' - a non-existant topic, which you can put pre-rolled relevance values
        The default value returned is 0, indicated no gain/non-relevant.

        topic_id (string): the TREC topic number
        doc_id (srting): the TREC document number
        """
        val = self._trecqrels.get_value_if_exists(topic_id, doc_id)  # Does the document exist?

        if not val:  # If not, we fall back to the generic topic.
            val = self._trecqrels.get_value('0', doc_id)
        if not val:  # if still no val, assume the document is not relevant.
            val = 0

        return val


    @abc.abstractmethod
    def is_relevant(self, document):
        """
        Needs to be implemented:
        Returns True if the document is considered relevant:
        else False.
        """
        pass

