from query_generators.base_generator import BaseQueryGenerator
from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from ifind.common.smoothed_language_model import BayesLanguageModel
from ifind.common.query_ranker import QueryRanker

class SingleTermQueryGenerator(BaseQueryGenerator):
    """
    A simple query generator - returns a set of queries consisting of only one term.
    These can be ranked by either the frequency of the term's occurrence, or by its perceived discriminatory value.
    """
    def __init__(self, output_controller, stopword_file, background_file=[], topic_model=0, log_queries=True):
        super(SingleTermQueryGenerator, self).__init__(output_controller, stopword_file, background_file=background_file, topic_model=topic_model)
        self.__log_queries = log_queries
    
    def generate_query_list(self, topic):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """
        topic_title = topic.title
        topic_background = topic.content
        
        topic_language_model = self._generate_topic_language_model(topic)
        
        generator = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        query_list = generator.extract_queries_from_text(topic_background)
        
        query_ranker = QueryRanker(smoothed_language_model=topic_language_model)
        query_ranker.calculate_query_list_probabilities(query_list)
        
        generated_queries = query_ranker.get_top_queries(100)
        
        if self.__log_queries:
            self._log_queries(generated_queries)
        
        return generated_queries
        
    def _generate_topic_language_model(self, topic):
        """
        Returns a languge model for the given topic, considering both the title and content text.
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