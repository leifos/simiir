__author__ = 'david'

import os
import redis
import cPickle
from ifind.seeker.trec_qrel_handler import TrecQrelHandler

class InformedFileDataHandler(object):
    """
    For file-based loading of the QRELs.
    """
    def __init__(self, filename, **kwargs):
        self._trecqrels = self._initialise_handler(filename)
    
    def _initialise_handler(self, filename, **kwargs):
        """
        Private method to initialise the QREL handler.
        Can be overriden by inheriting classes to read the handler from other sources.
        Must return an instance of a TrecQrelHandler.
        """
        
        import time
        start_time = time.time()
        handler = TrecQrelHandler(filename)
        print("--- %s seconds ---" % (time.time() - start_time))
        
        return handler
        
        
        #return TrecQrelHandler(filename)
    
    def get_value(self, topic_id, doc_id):
        """
        Given a topic and document ID (both as strings, returns the corresponding judgement for that topic/document combination).
        """
        return self._trecqrels.get_value_if_exists(topic_id, doc_id)


class InformedRedisDataHandler(InformedFileDataHandler):
    """
    For Redis-based storing of the QREL file.
    """
    def __init__(self, filename, host='localhost', port=6379):  # Defaults, assume localhost@6379 for Redis server.
                                                                # The BaseInformedTrecTextClassifier needs to be refactored to accomodate passing this information.
        self._trecqrels = self._initialise_handler(filename, host=host, port=port)
    
    def _initialise_handler(self, filename, **kwargs):
        """
        Overrides the base handler. Attempts to load the TrecQrelHandler from Redis (pickled).
        If it does not exist, the base method is called to construct a TrecQrelHandler, and stores it in the cache.
        """
        key = os.path.split(filename)[1]  # Better way to construct a key, from the file hash or something?
                                          # At present, it simply strips the filename from the string.
        cache = redis.StrictRedis(host=kwargs['host'], port=kwargs['port'], db=0)
        
        if cache.get(key):
            dumped = cache.get(key)
            return cPickle.loads(dumped)
        
        # The Redis key does not exist; we need to create the TrecQrelHandler and dump it to the cache.
        handler = super(InformedRedisDataHandler, self)._initialise_handler(filename)
        dumped = cPickle.dumps(handler)
        cache.set(key, dumped)
        
        return handler