from query_generators.tri_term_generator import TriTermQueryGenerator

class TriTermQueryGeneratorReversed(TriTermQueryGenerator):
    """
    Implementing Strategy 3 from Heikki's 2009 paper, generating three-term queries.
    The first two terms are drawn from the topic, with the final and third term selected from the description - in some ranked order.
    Reverses the queries.
    """
    def __init__(self, output_controller, stopword_file, background_file=[], topic_model=0, log_queries=True):
        super(TriTermQueryGeneratorReversed, self).__init__(output_controller, stopword_file, background_file=background_file, topic_model=topic_model, log_queries=False)
        self.__log_queries = log_queries
    
    def generate_query_list(self, topic):
        """
        Takes the query list from the underlying query generator (tri-term), and reverses it.
        """
        queries = super(TriTermQueryGeneratorReversed, self).generate_query_list(topic)
        queries.reverse()
        
        if self.__log_queries:
            self._log_queries(queries)
        
        return queries