from simiir.query_generators.single_term_generator import SingleTermQueryGenerator

class SingleTermQueryGeneratorReversed(SingleTermQueryGenerator):
    """
    Single-term query generator, returning a query list in reverse order (i.e. poorer queries first).
    """
    def __init__(self, output_controller, stopword_file, background_file=[]):
        super(SingleTermQueryGeneratorReversed, self).__init__(output_controller, stopword_file, background_file=background_file)
    
    def generate_query_list(self, topic, search_context=None):
        """
        Takes the query list from the underlying query generator (single term), and reverses it.
        """
        queries = super(SingleTermQueryGeneratorReversed, self).generate_query_list(topic)
        queries.reverse()
        
        self._log_queries(queries)
        
        return queries