import abc
from ifind.common.language_model import LanguageModel

class BaseTextClassifier(object):
    """
    """
    def __init__(self, topic, search_context, stopword_file=[], background_file=[]):  # Refactor; is this the best way to pass in details?
        self._stopword_file = stopword_file
        self._background_file = background_file
        self._topic = topic
        self._search_context = search_context
        self.doc_score = 0.0
        self.updating = False
        self.update_method = 1
        
        if self._background_file:
            self.read_in_background(self._background_file)
    
    #@abc.abstractmethod
    def is_relevant(self, document):
        """
        Returns True if the given document is relevant.
        This is an abstract method; override this method with an inheriting text classifier.
        """
        return True
    
    def read_in_background(self, vocab_file):
        """
        Helper method to read in a file containing terms and construct a background language model.
        """
        vocab = {}
        f = open(vocab_file, 'r')
        
        for line in f:
            tc = line.split(',')
            vocab[tc[0]] = int(tc[1])
        
        f.close()
        self.background_language_model = LanguageModel(term_dict=vocab)


    def update_model(self, search_context):
        """
        Enables the model of relevance/topic to be updated, based on the search context
        The update model based on the documents etc in the search context (i.e. memory of the user)

        :param  search_context: search_contexts.search_context object
        :return: returns True is topic model is updated.
        """
        return False
