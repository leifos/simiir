__author__ = 'leif'
from text_classifiers.base_classifier import BaseTextClassifier
import logging

log = logging.getLogger('trec_classifer.TrecTextClassifier')



class TrecTextClassifier(BaseTextClassifier):
    """

    """
    def __init__(self, topic, search_context, stopword_file=[], background_file=[]):
        """

        """
        super(TrecTextClassifier, self).__init__(topic, search_context, stopword_file, background_file)

    def make_topic_language_model(self):
        """

        """
        log.debug("No Topic model required for Trec Classifier: It always returns true")

    def is_relevant(self, document):
        """
        Every snippet/document is considered relevant
        """
        return True

