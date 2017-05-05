__author__ = 'david'

from ifind.common.language_model import LanguageModel
from simiir.text_classifiers.lm_classifier import LMTextClassifier
from simiir.utils.lm_methods import extract_term_dict_from_text
import logging

log = logging.getLogger('lm_classifer.TopicBasedLMTextClassifier')

class TopicBasedLMTextClassifier(LMTextClassifier):
    """
    Extends the LM text classifier, but also considers topic background knowledge (if provided).
    """
    def __init__(self, topic, search_context, stopword_file=[], background_file=[], topic_weighting=1, topic_background_weighting=1, document_weighting=1):
        self.topic_weighting = topic_weighting  # Weighting score for topic text
        self.topic_background_weighting = topic_background_weighting  # Weighting score for background topic text
        self.document_weighting = document_weighting  # Weighting score for examined snippet text
        
        super(TopicBasedLMTextClassifier, self).__init__(topic, search_context, stopword_file, background_file)
    
    def make_topic_language_model(self):
        """
        Combines term counts from the topic and background to produce the language model.
        """
        topic_text = self._make_topic_text()
        
        # Get term counts from the TREC topic title and description.
        topic_terms = extract_term_dict_from_text(topic_text, self._stopword_file)
        
        # Get term counts from the topic background.
        background_terms = self._topic.background_terms
        
        combined_term_counts = {}
        combined_term_counts = self._combine_dictionaries(combined_term_counts, topic_terms, self.topic_weighting)
        combined_term_counts = self._combine_dictionaries(combined_term_counts, background_terms, self.topic_background_weighting)
        
        # Build the LM from the combined count dictionary.
        language_model = LanguageModel(term_dict=combined_term_counts)
        self.topic_language_model = language_model

        log.debug("Making topic {0}".format(self._topic.id))

    def _update_topic_language_model(self, text_list):
        """
        Updates the language model for the topic, given snippet/document text (text_list) and prior (knowledge) text.
        """
        topic_text = self._make_topic_text()
        document_text = ' '.join(text_list)
        
        topic_term_counts = extract_term_dict_from_text(topic_text, self._stopword_file)
        background_scores = self._topic.background_terms
        document_term_counts = extract_term_dict_from_text(document_text, self._stopword_file)
        
        combined_term_counts = {}
        combined_term_counts = self._combine_dictionaries(combined_term_counts, topic_term_counts, self.topic_weighting)
        combined_term_counts = self._combine_dictionaries(combined_term_counts, background_scores, self.topic_background_weighting)
        combined_term_counts = self._combine_dictionaries(combined_term_counts, document_term_counts, self.document_weighting)
        
        # Build the updated language model.
        new_language_model = LanguageModel(term_dict=combined_term_counts)
        self.topic_language_model = new_language_model
        log.debug("Updating topic {0}".format(self._topic.id))
    
    def _combine_dictionaries(self, src_dict, from_dict, weight):
        """
        Takes from_dict, and multiples the values in that dictionary by weight, adding them to src_dict.
        """
        for term, value in from_dict.iteritems():
            weighted_score = value * weight
            
            if term not in src_dict:
                src_dict[term] = 0.0  # Create a zero value so then we only add it once below
            
            src_dict[term] += weighted_score
        
        return src_dict