__author__ = 'david'

from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from simiir.text_classifiers.lm_classifier import LMTextClassifier
from simiir.utils.lm_methods import extract_term_dict_from_text
import logging

log = logging.getLogger('lm_classifer.TopicBasedLMTextClassifier')

class TopicBasedLMTextClassifier(LMTextClassifier):
    """
    Extends the LM text classifier, but also considers topic background knowledge (if provided).
    """
    def __init__(self, topic, stopword_file=[], background_file=[]):
        self.topic_weighting = 2  # Weighting score for topic text
        self.background_weighting = 1  # Weighting score for background topic text
        self.document_weighting = 1  # Weighting score for examined snippet text

        super(TopicBasedLMTextClassifier, self).__init__(topic, stopword_file, background_file)


    def make_topic_language_model(self):
        """
        Combines term counts from the topic and background to produce the language model.
        """
        topic_text = self._make_topic_text() * self.topic_weighting
        background_text = self._topic.background_terms * self.background_weighting

        term_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        
        # Get term counts from the TREC topic title and description.
        term_extractor.extract_queries_from_text(topic_text)
        topic_term_counts = term_extractor.query_count
        
        # Get term counts from the background text. This is an emptystring if no background is provided.
        term_extractor.extract_queries_from_text(background_text)
        background_term_counts = term_extractor.query_count
        
        # Combine the two count dictionaries together into one dictionary.
        combined_term_counts = background_term_counts.copy()
        
        for k, v in topic_term_counts.iteritems():
            if k not in combined_term_counts:
                combined_term_counts[k] = v
            
            combined_term_counts[k] += v
        
        # Build the LM from the combined count dictionary.
        language_model = LanguageModel(term_dict=combined_term_counts)
        self.topic_language_model = language_model

        log.debug("Making topic {0}".format(self._topic.id))

    def _update_topic_language_model(self, text_list):
        """
        Updates the language model for the topic, given snippet/document text (text_list) and prior (knowledge) text.
        """
        topic_text = self._make_topic_text(document_text=text_list) * self.topic_weighting
        background_text = self._topic.background_terms * self.background_weighting
        document_text = ' '.join(text_list) * self.document_weighting
        
        term_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        
        # Get term counts from the TREC topic title and description.
        term_extractor.extract_queries_from_text(topic_text)
        topic_term_counts = term_extractor.query_count
        
        # Get term counts from the background text. This is an emptystring if no background is provided.
        term_extractor.extract_queries_from_text(background_text)
        background_term_counts = term_extractor.query_count
        
        # Get term counts from the observed snippet/document text.
        term_extractor.extract_queries_from_text(document_text)
        document_term_counts = term_extractor.query_count
        
        # Combine the three count dictionaries together into one dictionary.
        combined_term_counts = background_term_counts.copy()
        
        for k, v in topic_term_counts.iteritems():
            if k not in combined_term_counts:
                combined_term_counts[k] = v
            
            combined_term_counts[k] += v
        
        for k, v in document_term_counts.iteritems():
            if k not in combined_term_counts:
                combined_term_counts[k] = v
            
            combined_term_counts[k] += v
        
        # Build the updated language model.
        new_language_model = LanguageModel(term_dict=combined_term_counts)
        self.topic_language_model = new_language_model
        log.debug("Updating topic {0}".format(self._topic.id))