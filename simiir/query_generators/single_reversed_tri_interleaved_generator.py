from ifind.common.query_ranker import QueryRanker
from ifind.common.query_generation import SingleQueryGeneration
from simiir.query_generators.base_generator import BaseQueryGenerator

from query_generators.single_term_generator_reversed import SingleTermQueryGeneratorReversed
from query_generators.tri_term_generator import TriTermQueryGenerator

class SingleReversedTriInterleavedQueryGenerator(BaseQueryGenerator):
    """
    Takes the SingleTermGeneratorReversed and the TriTermGenerator, and interleaves like [Single,Tri,Single,Tri,Single,Tri...]
    """
    def __init__(self, stopword_file, background_file=[]):
        super(SingleReversedTriInterleavedQueryGenerator, self).__init__( stopword_file, background_file=background_file)
        self.__single = SingleTermQueryGeneratorReversed( stopword_file, background_file)
        self.__tri = TriTermQueryGenerator(stopword_file, background_file)

    def generate_query_list(self, search_context):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """
        topic = search_context.topic
        single_queries = self.__single.generate_query_list(search_context)
        tri_queries = self.__tri.generate_query_list(search_context)
        interleaved_queries = [val for pair in zip(single_queries, tri_queries) for val in pair]

        return interleaved_queries
