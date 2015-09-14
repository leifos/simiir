from query_generators.single_term_generator import SingleTermQueryGenerator

class SingleTermQueryGeneratorReversed(SingleTermQueryGenerator):
    """
    Single-term query generator, returning a query list in reverse order (i.e. poorer queries first).
    """
    def __init__(self, output_controller, stopword_file, background_file=[], topic_model=0, log_queries=True):
        super(SingleTermQueryGeneratorReversed, self).__init__(output_controller, stopword_file, background_file=background_file, topic_model=topic_model, log_queries=False)
        self.__log_queries = log_queries
    
    def generate_query_list(self, topic):
        """
        Takes the query list from the underlying query generator (single term), and reverses it.
        """
        queries = super(SingleTermQueryGeneratorReversed, self).generate_query_list(topic)
        queries.reverse()
        
        if self.__log_queries:
            self._log_queries(queries)
        
        return queries