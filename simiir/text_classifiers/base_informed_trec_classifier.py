__author__ = 'david'

import abc
from simiir.text_classifiers.base_classifier import BaseTextClassifier
from simiir.utils.data_handlers import get_data_handler
from random import random
import logging

log = logging.getLogger('base_informed_trec_classifier')

class BaseInformedTrecTextClassifier(BaseTextClassifier):
    """
    Takes the TREC QREL file and loads it into a TrecQrelHandler

    Abstract method is_relevant() needs to be implemented.
    """
    def __init__(self, topic, search_context, qrel_file, host=None, port=0):
        """
        Initialises an instance of the classifier.
        """
        super(BaseInformedTrecTextClassifier, self).__init__(topic, search_context, stopword_file=[], background_file=[])
        self._filename = qrel_file
        self._host = host
        self._port = port
        self._data_handler = get_data_handler(filename=self._filename, host=self._host, port=self._port, key_prefix='informed')
    
    
    def make_topic_language_model(self):
        """
        
        """
        log.debug("No Topic model required for this TREC Classifier")
    
    
    def _get_judgment(self, topic_id, doc_id):
        """
        Helper function that returns the judgement of the document
        If the value does not exist in the qrels, it checks topic '0' - a non-existant topic, which you can put pre-rolled relevance values
        The default value returned is 0, indicated no gain/non-relevant.

        topic_id (string): the TREC topic number
        doc_id (srting): the TREC document number
        """
        val = self._data_handler.get_value(topic_id, doc_id)  # Does the document exist?
                                                              # Pulls the answer from the data handler.

        if not val:  # If not, we fall back to the generic topic.
            val = self._data_handler.get_value('0', doc_id)
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

