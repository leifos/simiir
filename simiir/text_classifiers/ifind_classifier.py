import math
from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from ifind.common.smoothed_language_model import SmoothedLanguageModel
from simiir.search_contexts import search_context
from simiir.text_classifiers.base_classifier import BaseTextClassifier
import logging

log = logging.getLogger('ifind_classifer.IFindTextClassifier')


class IFindTextClassifier(BaseTextClassifier):
    """
    
    """
    def __init__(self, topic, search_context, stopword_file=[], background_file=[]):
        """
        
        """
        super(IFindTextClassifier, self).__init__(topic, search_context, stopword_file, background_file)
        self.threshold = 0.0
        self.mu = 100.0
        self.make_topic_language_model()


    
    def make_topic_language_model(self):
        """
        
        """
        topic_text = '{title} {title} {title} {content}'.format(**self._topic.__dict__)

        document_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        document_extractor.extract_queries_from_text(topic_text)
        document_term_counts = document_extractor.query_count
        
        language_model = LanguageModel(term_dict=document_term_counts)

        self.topic_language_model = SmoothedLanguageModel(language_model, self.background_language_model, self.mu)
        log.debug("Making topic {0}".format(self.topic_language_model.docLM.total_occurrences))
    
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

        self.doc_score = (score/count)
        if self.doc_score > self.threshold:
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
            return math.log(topic_term_prob/background_term_prob, 2.0)


    def update_model(self, search_context):

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
                self.__update_topic_language_model(rel_text_list)
                return True
            else:
                return False

    def __update_topic_language_model(self, text_list):

        topic_text =  '{title} {title} {title} {content}'.format(**self._topic.__dict__)

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

        self.topic_language_model = SmoothedLanguageModel(new_language_model, self.background_language_model, self.mu)



        log.debug("Updating topic {0}".format(self._topic.id))
