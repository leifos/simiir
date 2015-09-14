__author__ = 'leif'

import os
import redis
import cPickle
from text_classifiers.base_informed_trec_classifier import BaseInformedTrecTextClassifier
from ifind.seeker.trec_qrel_handler import TrecQrelHandler
from random import random

class RedisInformedTrecTextClassifier(BaseInformedTrecTextClassifier):
    """
    A concrete implementation of BaseInformedTrecTextClassifier.
    Loads QRELS from a Redis cache, or if it does not exist in the cache, from disk.
    """
    def __init__(self, topic, qrel_file, stopword_file=[], background_file=[], rprob=1.0, nprob=1.0, host='localhost', port=6379, key_base='{0}'):
        """
        Initialises the Redis cache and underlying code for the InformedTextClassifier.
        """
        self.__cache = redis.StrictRedis(host=host, port=port, db=0)
        self.__key_base = key_base
        super(RedisInformedTrecTextClassifier, self).__init__(topic, qrel_file, stopword_file, background_file, rprob=rprob, nprob=nprob)
        
    
    def _initialise_handler(self, qrel_file):
        """
        This is spun off from the constructor to make way for the Redis classifier.
        Contrete implementation of the base class!
        """
        filename = os.path.basename(qrel_file)
        key = self.__key_base.format(filename)
        
        if self.__cache.get(key):
            dumped = self.__cache.get(key)
            handler = cPickle.loads(dumped)
        else:
            handler = TrecQrelHandler(qrel_file)
            dumped = cPickle.dumps(handler)
            
            self.__cache.set(key, dumped)
            
        self._trecqrels = handler