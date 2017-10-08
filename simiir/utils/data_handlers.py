__author__ = 'David'
__version__ = 2


import os
import redis
import base64
import cPickle
from ifind.seeker.trec_qrel_handler import TrecQrelHandler


#
# Revised datahandler classes -- considering code refactoring in September 2017.
# Author: David Maxwell
# Date: 2017-09-24
#


def get_data_handler(filename=None, host=None, port=None, key_prefix=None):
    """
    Factory function that returns an instance of a data handler class.
    The exact type instantiated depends upon the arguments provided to the function.
    If an invalid combination is supplied, a ValueError exception is raised.
    """
    if filename is None:
        raise ValueError("You need to supply a filename for a data handler to work.")
    
    if host is not None:
        if port is None or key_prefix is None:
            raise ValueError("Please supply a host, port and key prefix for the redis handler.")
        
        # All parameters are correct for a RedisDataHandler to be constructed.
        return RedisDataHandler(filename=filename, host=host, port=port, key_prefix=key_prefix)
    
    # If we get here, we will simply return a FileDataHandler.
    # No other option exists.
    return FileDataHandler(filename=filename)


class FileDataHandler(object):
    """
    A simple, file-based data handler.
    Assumes that the filename provided points to a TREC QREL formatted file.
    """
    def __init__(self, filename):
        self._trec_qrels = self._initialise_handler(filename)
    
    
    def _initialise_handler(self, filename):
        """
        Instantiates the data handler object.
        Override this method to instantiate a different data handler, ensuring
        that a TrecQrelHandler is returned.
        """
        return TrecQrelHandler(filename)
    
    
    def get_value(self, topic_id, doc_id):
        """
        Given a topic and document combination, returns the corresponding
        judgement for that topic/document combination.
        """
        return self._trec_qrels.get_value_if_exists(topic_id, doc_id)
    
    
    def get_value_fallback(self, topic_id, doc_id):
        """
        Given a topic and document combination, returns the corresponding
        judgement for that topic/document combination.
        If the judgement does not exist, we fall back to the default topic of '0'.
        """
        val = self.get_value(topic_id, doc_id)  # Does the document exist?
                                                # Pulls the answer from the data handler.
        
        if not val:  # If not, we fall back to the generic topic.
            val = self.get_value('0', doc_id)
        if not val:  # if still no val, assume the document is not relevant.
            val = 0
        
        return val


class RedisDataHandler(FileDataHandler):
    """
    Extends the FileDataHandler to consider a TrecQrelHandler object stored in
    a Redis cache. If it is found that a TrecQrelHandler object does not exist for
    the given key, a new TrecQrelHandler is instantiated using the filename given.
    This handler is then placed in the Redis cache, ready for the next use.
    """
    def __init__(self, filename, host='localhost', port=6379, key_prefix=None):
        self._trec_qrels = self._initialise_handler(filename=filename, host=host, port=port, key_prefix=key_prefix)
    
    
    def _initialise_handler(self, filename, host, port, key_prefix):
        """
        Instantiates the handler if it is not in the cache, or loads from the cache if it is.
        """
        
        key = os.path.split(filename)[-1] # Is there a better way to construct a unique key?
                                          # Perhaps take the hash *from the file contents*.
                                          # At present, the filename seems sufficient.
        
        if key_prefix is None:
            raise ValueError("A key prefix (string) must be specified for the RedisDataHandler.")
        
        key = '{key_prefix}::{hashed_key}'.format(key_prefix=key_prefix, hashed_key=hash(key))
        
        cache = redis.StrictRedis(host=host, port=port, db=0)
        
        if cache.get(key):
            dumped = cache.get(key)
            return cPickle.loads(dumped)
        
        # If we get here, the TrecQrelsHandler does not exist in the cache; create it, dump it.
        handler = super(RedisDataHandler, self)._initialise_handler(filename)
        dumped = cPickle.dumps(handler)
        cache.set(key, dumped)
        
        return handler