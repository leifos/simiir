from query_generators.base_generator import BaseQueryGenerator

from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from ifind.common.smoothed_language_model import BayesLanguageModel

class SmarterQueryGenerator(BaseQueryGenerator):
    """
    
    """
    def _generate_topic_language_model(self, topic):
        """
        
        """
        topic_text = topic.title
        topic_background = topic.content
        
        document_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        document_extractor.extract_queries_from_text(topic_text)
        document_term_counts = document_extractor.query_count
        
        document_extractor.extract_queries_from_text(topic_background)
        
        background_term_counts = document_extractor.query_count
        
        title_language_model = LanguageModel(term_dict=document_term_counts)
        background_language_model = LanguageModel(term_dict=background_term_counts)
        topic_language_model = BayesLanguageModel(title_language_model, background_language_model, beta=10)
        return topic_language_model