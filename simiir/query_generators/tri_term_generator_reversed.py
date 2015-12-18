from simiir.query_generators.tri_term_generator import TriTermQueryGenerator

class TriTermQueryGeneratorReversed(TriTermQueryGenerator):
    """
    Implementing Strategy 3 from Heikki's 2009 paper, generating three-term queries.
    The first two terms are drawn from the topic, with the final and third term selected from the description - in some ranked order.
    Reverses the queries.
    """
    def __init__(self, stopword_file, background_file=[]):
        super(TriTermQueryGeneratorReversed, self).__init__(stopword_file, background_file=background_file)

    
    def generate_query_list(self, search_context):
        """
        Takes the query list from the underlying query generator (tri-term), and reverses it.
        """
        topic = search_context.topic
        queries = super(TriTermQueryGeneratorReversed, self).generate_query_list(search_context)
        queries.reverse()

        return queries