import math
from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from text_classifiers.base_classifier import BaseTextClassifier
from ifind.common.smoothed_language_model import SmoothedLanguageModel

class IFindTextClassifier(BaseTextClassifier):
    """
    
    """
    def __init__(self, topic, stopword_file=[], background_file=[]):
        """
        
        """
        super(IFindTextClassifier, self).__init__(topic, stopword_file, background_file)
        self.make_topic_language_model()
    
    def make_topic_language_model(self):
        """
        
        """
        topic_text = self._topic.content + self._topic.title
        
        document_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        document_extractor.extract_queries_from_text(topic_text)
        document_term_counts = document_extractor.query_count
        
        language_model = LanguageModel(term_dict=document_term_counts)
        self.topic_language_model = SmoothedLanguageModel(language_model, self.background_language_model, 100)
        print "making topic", self.topic_language_model.docLM.total_occurrences
    
    def is_relevant(self, document):
        """
        
        """
        score = 0.0
        count = 0.0
        
        for term in document.title.split(' '):
            score = score + self.__get_term_score(term)
            count = count + 1.0
        
        for term in document.content.split(' '):
            score = score + self.__get_term_score(term)
            count = count + 1.0
        
        if (score / count) > self.threshold:
            return True
        
        return False
    
    def __get_term_score(self, term):
        """
        Returns a probability score for the given term when considering both the background and topic language models.
        """
        topic_term_prob = self.topic_language_model.get_term_prob(term)
        background_term_prob = self.background_language_model.get_term_prob(term)
        
        if background_term_prob == 0.0:
            return 0.0
        else:
            return math.log(topic_term_prob/background_term_prob, 2)
        