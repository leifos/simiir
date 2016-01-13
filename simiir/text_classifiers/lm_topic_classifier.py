__author__ = 'david'

from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from simiir.text_classifiers.lm_classifier import LMTextClassifier
from simiir.utils.lm_methods import extract_term_dict_from_text
import logging

log = logging.getLogger('lm_classifer.TopicBasedLMTextClassifier')

class TopicBasedLMTextClassifier(LMTextClassifier):
    """

    """
    def __init__(self, topic, stopword_file=[], background_file=[]):
        self.prior_knowledge_filename = None
        self.topic_weighting = 1  # Weighting score for topic text
        self.prior_weighting = 1  # Weighting score for prior knowledge text
        self.document_weighting = 1  # Weighting score for examined snippet text

        super(TopicBasedLMTextClassifier, self).__init__(topic, stopword_file, background_file)


    def make_topic_language_model(self):
        """

        """
        if not hasattr(self, 'prior_knowledge'):
            self.prior_knowledge = self.read_prior_knowledge()

        topic_text = self._make_topic_text() * self.topic_weighting
        prior_text = self.prior_knowledge * self.prior_weighting

        term_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        term_extractor.extract_queries_from_text(topic_text)
        term_extractor.extract_queries_from_text(prior_text)
        document_term_counts = term_extractor.query_count

        language_model = LanguageModel(term_dict=document_term_counts)
        self.topic_language_model = language_model

        log.debug("Making topic {0}".format(self._topic.id))

    def _update_topic_language_model(self, text_list):
        """
        Updates the language model for the topic, given snippet/document text (text_list) and prior (knowledge) text.
        """
        topic_text = self._make_topic_text(document_text=text_list) * self.topic_weighting
        prior_text = self.prior_knowledge * self.prior_weighting

        snippet_text = ' '.join(text_list) * self.document_weighting

        term_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        term_extractor.extract_queries_from_text(topic_text)
        topic_term_counts = term_extractor.query_count

        term_extractor.extract_queries_from_text(snippet_text)
        term_extractor.extract_queries_from_text(prior_text)
        new_text_term_counts = term_extractor.query_count

        for term in topic_term_counts:
            if term in new_text_term_counts:
                new_text_term_counts[term] += topic_term_counts[term]
            else:
                new_text_term_counts[term] = topic_term_counts[term]

        new_language_model = LanguageModel(term_dict=new_text_term_counts)

        self.topic_language_model = new_language_model

        log.debug("Updating topic {0}".format(self._topic.id))


    def read_prior_knowledge(self):
        """
        Takes a file from word2vec, and returns a string of the terms appearing in the file.
        Assumes that each word is on a new line, with a score separated by commas. <TERM>,<SCORE>
        """
        if self.prior_knowledge_filename:
            f = open(self.prior_knowledge_filename, 'r')
            terms = []

            for line in f:
                line = line.strip().split(',')
                terms.append(line[0])

            f.close()
            return ' '.join(terms)

        # No knowledge specified; return emptystring.
        return ''