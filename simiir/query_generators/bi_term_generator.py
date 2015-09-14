from ifind.common.query_ranker import QueryRanker
from ifind.common.query_generation import SingleQueryGeneration
from query_generators.smarter_generator import SmarterQueryGenerator

class BiTermQueryGenerator(SmarterQueryGenerator):
    """
    Implementing Strategy 2 from Heikki's 2009 paper, generating two-term queries.
    The first term comes from the term ranked highest in the topic title, with the second term originating from the description.
    Currently uses a language model to perform the ranking of terms.
    """
    def generate_query_list(self, topic):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """
        self.__description_cutoff = 100
        
        topic_title = topic.title
        topic_description = topic.content
        topic_language_model = self._generate_topic_language_model(topic)
        
        # Generate a series of query terms from the title, and then rank the generated terms.
        title_generator = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        title_query_list = title_generator.extract_queries_from_text(topic_title)
        title_query_list = self._rank_terms(title_query_list, topic_language_model=topic_language_model)
        
        # Perform the same steps, but from the description of the topic.
        description_generator = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        description_query_list = description_generator.extract_queries_from_text(topic_description)
        description_query_list = self._rank_terms(description_query_list, topic_language_model=topic_language_model)
        
        generated_permutations = self.__generate_permutations(topic_language_model, title_query_list, description_query_list)
        self._log_queries(generated_permutations)
        return generated_permutations
    
    def _rank_terms(self, terms, **kwargs):
        """
        Ranks the query terms by their discriminatory power.
        The length of the list returned == list of initial terms supplied.
        """
        topic_language_model = kwargs.get('topic_language_model', None)
        
        ranker = QueryRanker(smoothed_language_model=topic_language_model)
        ranker.calculate_query_list_probabilities(terms)
        return ranker.get_top_queries(len(terms))
    
    def __generate_permutations(self, topic_language_model, title_query_list, description_query_list):
        """
        Returns a list of ranked permutations for each title term.
        Queries are ranked for each title term - this ensures that the sequence of w1 w2 > w1 w3 is not broken.
        """
        return_terms = []
        observed_stems = []
        
        for term in title_query_list:
            stemmed_term = self._stem_term(term[0])
            if stemmed_term not in observed_stems:
                observed_stems.append(stemmed_term)
        
        for title_term in title_query_list:
            title_terms = []
            cutoff_counter = 0
            
            for description_term in description_query_list:
                if self.__description_cutoff > 0 and cutoff_counter == self.__description_cutoff:
                    break
                
                stemmed_term = self._stem_term(description_term[0])
                if stemmed_term in observed_stems:
                    continue
                
                observed_stems.append(stemmed_term)
                title_terms.append('{0} {1}'.format(title_term[0], description_term[0]))
                
                cutoff_counter = cutoff_counter + 1
            
            title_terms = self._rank_terms(title_terms, topic_language_model=topic_language_model)
            return_terms = return_terms + title_terms
        
        return return_terms