from ifind.common.query_ranker import QueryRanker
from ifind.common.query_generation import SingleQueryGeneration
from query_generators.base_generator import BaseQueryGenerator

class PredeterminedQueryGenerator(BaseQueryGenerator):
    """
    Not really a query generator per se...
    but given a list of queries from a configuration file, returns the query list in the specified order.
    
    Requires the following attributes:
        stopword_file (required by all query generators, not used)
        query_file (string representing path to query file)
        user (string representing the user to focus on)
    
    The query file should be in the format (note CSV!)
        queryid,userid,topic,terms
    """
    def __init__(self, output_controller, stopword_file, query_file, user, background_file=[], topic_model=0):
        """
        Initialises the class.
        """
        super(PredeterminedQueryGenerator, self).__init__(output_controller, stopword_file, background_file=[], topic_model=0)
        self.__query_filename = query_file
        self.__user = user
    
    def generate_query_list(self, topic):
        """
        Returns the list of predetermined queries for the specified user.
        """
        queries = []
        queries_file = open(self.__query_filename, 'r')
        
        for line in queries_file:
            line = line.strip()
            line = line.split(',')
            
            line_qid = line[0]
            line_user = line[1]
            line_topic = line[2]
            line_terms = ' '.join(line[3:])
            
            if line_user == self.__user and line_topic == topic.id:
                queries.append((line_terms, int(line_qid)))
        
        queries_file.close()
        
        sorted(queries, key=lambda x: x[1])
        self._log_queries(queries)
        return queries