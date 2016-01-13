__author__ = 'leif'

from simiir.query_generators.base_generator import BaseQueryGenerator

from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from ifind.common.smoothed_language_model import BayesLanguageModel

class TrecTopicQueryGenerator(BaseQueryGenerator):
    """
        TREC topic Query - only generates one query from the topic title.
    """


    def generate_query_list(self, search_context):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.

        """
        topic = search_context.topic
        topic_text = topic.title

        return [ (topic_text, 1) ]
