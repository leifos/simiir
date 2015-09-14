from ifind.common.query_ranker import QueryRanker
from ifind.common.query_generation import SingleQueryGeneration
from query_generators.base_generator import BaseQueryGenerator

from query_generators.single_term_generator_reversed import SingleTermQueryGeneratorReversed
from query_generators.tri_term_generator_reversed import TriTermQueryGeneratorReversed

class SingleReversedTriReversedInterleavedGenerator(BaseQueryGenerator):
    """
    Takes the SingleTermGeneratorReversed and the TriTermGenerator, and interleaves like [Single,Tri,Single,Tri,Single,Tri...]
    """
    def __init__(self, output_controller, stopword_file, background_file=[], topic_model=0):
        super(SingleReversedTriReversedInterleavedGenerator, self).__init__(output_controller, stopword_file, background_file=background_file, topic_model=topic_model)
        self.__single = SingleTermQueryGeneratorReversed(output_controller, stopword_file, background_file, topic_model, log_queries=False)
        self.__tri = TriTermQueryGeneratorReversed(output_controller, stopword_file, background_file, topic_model, log_queries=False)
    
    def generate_query_list(self, topic):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """
        single_queries = self.__single.generate_query_list(topic)
        tri_queries = self.__tri.generate_query_list(topic)
        
        interleaved_queries = [val for pair in zip(single_queries, tri_queries) for val in pair]
        self._log_queries(interleaved_queries)
        
        return interleaved_queries

