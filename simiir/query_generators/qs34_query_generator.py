__author__ = 'leif'
from simiir.query_generators.base_generator import BaseQueryGenerator
from simiir.query_generators.smarter_generator import  SmarterQueryGenerator
from simiir.utils import lm_methods
from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from ifind.common.smoothed_language_model import BayesLanguageModel, SmoothedLanguageModel
from ifind.common.query_generation import SingleQueryGeneration, BiTermQueryGeneration, TriTermQueryGeneration
from ifind.common.query_ranker import QueryRanker
from bs4 import BeautifulSoup
import itertools


class QS34QueryGenerator(SmarterQueryGenerator):


    def __init__(self, stopword_file, background_file=None):
        super(QS34QueryGenerator, self).__init__(stopword_file, background_file=background_file)
        self.topic_lang_model = None
        self.title_weight = 3



    def generate_query_list(self, search_context):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """

        topic_text = search_context.topic.get_topic_text()
        if self.topic_lang_model is None:
            self.topic_lang_model = self._generate_topic_language_model(search_context)


        snip_text = self._get_snip_text(search_context)

        all_text = topic_text + ' ' + snip_text

        all_text = self._check_terms(all_text)


        term_list = all_text.split(' ')
        term_list = list(set(term_list))


        q3_list = list(itertools.combinations(term_list,3))
        q4_list = list(itertools.combinations(term_list,4))

        query_list = []

        for q in q3_list:
            query_list.append( ' '.join(q))

        for q in q4_list:
            query_list.append( ' '.join(q))




        query_ranker = QueryRanker(smoothed_language_model=self.topic_lang_model)
        query_ranker.calculate_query_list_probabilities(query_list)
        gen_query_list = query_ranker.get_top_queries(100)


        return gen_query_list