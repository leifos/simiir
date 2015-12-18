from simiir.query_generators.single_term_generator import SingleTermQueryGenerator

class SingleTermQueryGeneratorReversed(SingleTermQueryGenerator):
    """
    Single-term query generator, returning a query list in reverse order (i.e. poorer queries first).
    """
    def __init__(self, stopword_file, background_file=[]):
        super(SingleTermQueryGeneratorReversed, self).__init__(stopword_file, background_file=background_file)
    
    def generate_query_list(self, search_context):
        """
        Takes the query list from the underlying query generator (single term), and reverses it.
        """
        topic = search_context.topic
        queries = super(SingleTermQueryGeneratorReversed, self).generate_query_list(search_context)
        queries.reverse()

        return queries