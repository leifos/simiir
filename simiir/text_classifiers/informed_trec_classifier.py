__author__ = 'leif'

from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from simiir.text_classifiers.base_informed_trec_classifier import BaseInformedTrecTextClassifier

import logging

log = logging.getLogger('informed_trec_classifer.InformedTrecTextClassifier')


class InformedTrecTextClassifier(BaseInformedTrecTextClassifier):
    """
    A concrete implementation of BaseInformedTrecTextClassifier.
    Loads QRELS from disk.
    """
    def __init__(self, topic, qrel_file, stopword_file=[], background_file=[], rprob=1.0, nprob=1.0):
        """

        """
        super(InformedTrecTextClassifier, self).__init__(topic, qrel_file, stopword_file, background_file, rprob=rprob, nprob=nprob)

        log.debug("Classifier uses TREC qrels to make decision:")


    
    def _initialise_handler(self, qrel_file):
        """
        This is spun off from the constructor to make way for the Redis classifier.
        Contrete implementation of the base class!
        """
        self._trecqrels = TrecQrelHandler(qrel_file)  # Easy!


    def is_relevant(self, document):
        """

        """
        val = self._trecqrels.get_value_if_exists(self._topic.id, document.doc_id)  # Does the document exist?

        if not val:  # If not, we fall back to the generic topic.
            return False
        else:
            if val > 0:
                return True
            else:
                return False