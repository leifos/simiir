from ifind.common.query_ranker import QueryRanker
from ifind.common.query_generation import SingleQueryGeneration
from simiir.utils import lm_methods
from simiir.query_generators.base_generator import BaseQueryGenerator

class TriTermQueryGenerator(BaseQueryGenerator):
    """
    Implementing Strategy 3 from Heikki's 2009 paper, generating three-term queries.
    The first two terms are drawn from the topic, with the final and third term selected from the description - in some ranked order.
    """
    def __init__(self, stopword_file, background_file=[]):
        super(TriTermQueryGenerator, self).__init__(stopword_file, background_file=background_file)

    
    def generate_query_list(self, search_context):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """
        self.__description_cutoff = 0

        topic = search_context.topic
        topic_title = topic.title
        topic_description = topic.content
        topic_language_model = self._generate_topic_language_model(search_context)
        
        # Generate a series of query terms from the title, and then rank the generated terms.
        title_generator = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        title_query_list = title_generator.extract_queries_from_text(topic_title)
        title_query_list = self._rank_terms(title_query_list, topic_language_model=topic_language_model)
        
        # Produce the two-term query "stem"
        title_query_list = self.__get_title_combinations(topic_language_model, title_query_list)
        
        # Perform the same steps, but from the description of the topic.
        description_generator = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        description_query_list = description_generator.extract_queries_from_text(topic_description)
        description_query_list = self._rank_terms(description_query_list, topic_language_model=topic_language_model)
        
        generated_permutations = self.__generate_permutations(topic_language_model, title_query_list, description_query_list)

        
        return generated_permutations
    
    def _rank_terms(self, terms, **kwargs):
        """
        Ranks terms according to their discriminatory power.
        """
        return lm_methods.rank_terms(terms, **kwargs)
    
    def __get_title_combinations(self, topic_language_model, title_query_list):
        """
        Returns a list of two-term ranked queries, extracted from the topic title.
        If the title consists of one term...surely not!!
        """
        count = 0
        prev_term = None
        windows = []
        
        if len(title_query_list) == 1:  # One term only, no need to do sliding windows.
            return title_query_list
        
        for term in title_query_list:
            if count == 0:
                prev_term = term[0]
                count = count + 1
                continue
            else:
                count = 0
                windows.append('{0} {1}'.format(prev_term, term[0]))
        
        return self._rank_terms(windows, topic_language_model=topic_language_model)
    
    def __generate_permutations(self, topic_language_model, title_query_list, description_query_list):
        """
        Returns a list of ranked permutations for each title term.
        Queries are ranked for each title term - this ensures that the sequence of w1 w2 > w1 w3 is not broken.
        """
        return_terms = []
        observed_stems = []
        
        # Hack - this should be an instance variable or something that can be shared between the title and description parts.
        for terms in title_query_list:
            for term in terms[0].split():
                stemmed_term = self._stem_term(term)
                
                if stemmed_term not in observed_stems:
                    observed_stems.append(stemmed_term)
        
        if len(observed_stems) == 1:
            get_terms = 2  # Indicate that we need to pull out two terms to compensate
        else:
            get_terms = 1  # Our pivot is of length 2; just get one term.
        
        for title_term in title_query_list:
            title_terms = []
            cutoff_counter = 0
            
            description_two = []
            
            for description_term in description_query_list:
                if self.__description_cutoff > 0 and cutoff_counter == self.__description_cutoff:
                    break
                
                stemmed_term = self._stem_term(description_term[0])
                if stemmed_term in observed_stems:
                    continue
                
                observed_stems.append(stemmed_term)
                
                if get_terms == 2:
                    if len(description_two) == 2:
                        title_terms.append('{0} {1} {2}'.format(title_term[0], description_two[0], description_two[1]))
                        description_two = [description_term[0]]
                    else:
                        description_two.append(description_term[0])
                else:
                    title_terms.append('{0} {1}'.format(title_term[0], description_term[0]))
                
                cutoff_counter = cutoff_counter + 1
            
            title_terms = self._rank_terms(title_terms, topic_language_model=topic_language_model)
            return_terms = return_terms + title_terms
        

        return return_terms