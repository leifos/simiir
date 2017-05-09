from simiir.query_generators.smarter_generator import SmarterQueryGenerator

class RefiningSmarterQueryGenerator(SmarterQueryGenerator):
    """
    
    """
    
    def __init__(self, stopword_file, background_file=None):
        super(RefiningSmarterQueryGenerator, self).__init__(stopword_file, background_file=background_file)
        self.topic_lang_model = None
        self.title_weight = 3
    
    def generate_query_list(self, search_context):
        """
        Calls the SmarterQueryGenerator, and manipulates the list depending upon the query number for the session.
        Guaranteed to start with two single-term queries, before posing a two-term query, with subsequent queries
        based upon the SmarterQueryGenerator. Mimics a couple of poor queries before the user gets up to speed.
        """
        smarter_query_list = super(RefiningSmarterQueryGenerator, self).generate_query_list(search_context)
        new_query_list = []
        query_count = search_context.get_session_query_count()
        start_at = 0
        
        for query_tuple in smarter_query_list:
            split_terms = query_tuple[0].split(' ')
            
            if len(split_terms) == 2:
                new_query_list.append((split_terms[0], 0.0))
                new_query_list.append((split_terms[1], 0.0))
                new_query_list.append(query_tuple)
                start_at = smarter_query_list.index(query_tuple) + 1
                break
        
        new_query_list = new_query_list + smarter_query_list[start_at:]
        return new_query_list