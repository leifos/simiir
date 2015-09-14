__author__ = 'leif'

from query_generators.base_generator import BaseQueryGenerator

from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from ifind.common.smoothed_language_model import BayesLanguageModel

class TrecTopicQueryGenerator(BaseQueryGenerator):
    """
        TREC topic Query - only generates one query.
    """


    def generate_query_list(self, topic):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.

        """
        topic_text = topic.title
        self._log_queries([(topic_text, 1)])
        return [ (topic_text, 1) ]


    def _generate_topic_language_model(self, topic):
        """

        """
        return None