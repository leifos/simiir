__author__ = 'leif'
import math
from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from simiir.text_classifiers.base_classifier import BaseTextClassifier
from ifind.common.smoothed_language_model import SmoothedLanguageModel
from simiir.utils.tidy import clean_html
from simiir.utils.lm_methods import extract_term_dict_from_text
import logging

log = logging.getLogger('lm_classifer.LMTextClassifier')


class LMTextClassifier(BaseTextClassifier):
    """

    """
    def __init__(self, topic, search_context, stopword_file=[], background_file=[]):
        """

        """
        super(LMTextClassifier, self).__init__(topic, search_context, stopword_file, background_file)
        self.alpha = 1.0
        self.lam = 0.1
        self.mu = 100.0
        self.threshold = 0.0
        self.method = 'jm'
        self.doc_score = 0.0
        self.updating = False
        self.title_weight = 1
        self.title_only = False
        self.make_topic_language_model()


    def _make_topic_text(self, **kwargs):
        """
        Returns a string representing the TREC topic information.
        Note that the attribute title_weight influences the weighting of the title.
        """
        title_text = '{0} '.format(self._topic.title) * self.title_weight
        topic_text = '{0} {1}'.format(title_text,self._topic.content)
        return topic_text


    def make_topic_language_model(self):
        """
        Generates a topic language model.
        """
        topic_text = self._make_topic_text()
        document_term_counts = extract_term_dict_from_text(topic_text, self._stopword_file)

        language_model = LanguageModel(term_dict=document_term_counts)
        self.topic_language_model = language_model

        #SmoothedLanguageModel(language_model, self.background_language_model, 100)
        log.debug("Making topic {0}".format(self._topic.id))


    def update_model(self, search_context):
        """
        If updating is enabled, updates the underlying language model with the new snippet/document text.
        Returns True iif the language model is updated; False otherwise.

        When self.update_method==1, documents are considered; else snippets.
        """
        if self.updating:
            ## Once we develop more update methods, it is probably worth making this a strategy
            ## so that setting the update_method changes the list of documents to use.
            if self.update_method == 1:
                document_list = search_context.get_all_examined_documents()
            else:
                document_list = search_context.get_all_examined_snippets()

            # iterate through document_list, pull out relevant snippets / text
            rel_text_list = []
            for doc in document_list:
                if doc.judgment > 0:
                    rel_text_list.append('{0} {1}'.format(doc.title, doc.content))
            if rel_text_list:
                self._update_topic_language_model(rel_text_list)
                return True
            else:
                return False

        return False

    def _update_topic_language_model(self, text_list):
        topic_text = self._make_topic_text(document_text=text_list)

        n = len(text_list)
        snippet_text = ' '.join(text_list)

        term_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        term_extractor.extract_queries_from_text(topic_text)
        topic_term_counts = term_extractor.query_count

        term_extractor.extract_queries_from_text(snippet_text)
        new_text_term_counts = term_extractor.query_count

        for term in topic_term_counts:
            if term in new_text_term_counts:
                new_text_term_counts[term] += topic_term_counts[term]
            else:
                new_text_term_counts[term] = topic_term_counts[term]

        new_language_model = LanguageModel(term_dict=new_text_term_counts)

        self.topic_language_model = new_language_model

        log.debug("Updating topic {0}".format(self._topic.id))



    def is_relevant(self, document):
        """

        """
        score = 0.0
        count = 0.0
        
        title_stripped = clean_html(document.title)
        content_stripped = clean_html(document.content)
        
        for term in title_stripped:
            score = score + self.get_term_score(term)
            count = count + 1.0
        
        if not self.title_only:
            for term in content_stripped:
                score = score + self.get_term_score(term)
                count = count + 1.0
        
        self.doc_score = (score/count)
        if self.doc_score > self.threshold:
            return True
        
        return False
    
    def get_term_score(self, term):
        """
        Returns a probability score for the given term when considering both the background and topic language models.
        """

        switch = {'jm': self.__get_jm_term_score,
                  'bs': self.__get_bs_term_score,
                  'lp': self.__get_lp_term_score
                  }


        return switch[self.method](term)



    def __get_jm_term_score(self, term):
        topic_term_prob = self.topic_language_model.get_term_prob(term)
        background_term_prob = self.background_language_model.get_term_prob(term)

        term_score = self.lam * topic_term_prob + (1.0-self.lam) * background_term_prob
        if term_score > 0.0 and background_term_prob > 0.0:
            return math.log(term_score/background_term_prob,2.0)
        else:
            return 0.0

    def __get_bs_term_score(self, term):
        topic_term_count = self.topic_language_model.get_num_occurrences(term)
        background_term_prob = self.background_language_model.get_term_prob(term)

        n = self.topic_language_model.get_total_occurrences()
        term_score =  (topic_term_count + self.mu * background_term_prob)/(n+self.mu)
        if term_score > 0.0 and background_term_prob > 0.0:
            return math.log(term_score/background_term_prob,2.0)
        else:
            return 0.0


    def __get_lp_term_score(self, term):
        topic_term_count = self.topic_language_model.get_num_occurrences(term)
        background_term_prob = self.background_language_model.get_term_prob(term)


        v = self.background_language_model.get_num_terms()
        n = self.topic_language_model.get_total_occurrences()

        if background_term_prob == 0.0:
            background_term_prob = 1.0/float(v);
        term_score = (float(topic_term_count) + float(self.alpha))/(float(n) + float(v)*float(self.alpha))
        if term_score > 0.0 and background_term_prob > 0.0:
            return math.log(term_score/background_term_prob,2.0)
        else:
            return 0.0








