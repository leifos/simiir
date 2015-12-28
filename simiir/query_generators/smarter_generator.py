from simiir.query_generators.base_generator import BaseQueryGenerator
from ifind.common.language_model import LanguageModel
from ifind.common.query_generation import SingleQueryGeneration
from ifind.common.smoothed_language_model import BayesLanguageModel
from ifind.common.query_generation import SingleQueryGeneration, BiTermQueryGeneration, TriTermQueryGeneration
from ifind.common.query_ranker import QueryRanker

class SmarterQueryGenerator(BaseQueryGenerator):
    """
    
    """

    def __init__(self, stopword_file, background_file=[]):
        super(SmarterQueryGenerator, self).__init__(stopword_file, background_file=background_file)
        self.topic_lang_model = None


    def _generate_topic_language_model(self, search_context):
        """
        
        """

        topic = search_context.topic
        topic_text = topic.title
        topic_background = topic.content
        
        document_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        document_extractor.extract_queries_from_text(topic_text)
        document_term_counts = document_extractor.query_count
        
        document_extractor.extract_queries_from_text(topic_background)
        
        background_term_counts = document_extractor.query_count
        
        title_language_model = LanguageModel(term_dict=document_term_counts)
        background_language_model = LanguageModel(term_dict=background_term_counts)
        topic_language_model = BayesLanguageModel(title_language_model, background_language_model, beta=10)
        return topic_language_model


    def generate_query_list(self, search_context):
        """
        Given a Topic object, produces a list of query terms that could be issued by the simulated agent.
        """

        topic_text = self.__get_topic_text(search_context)
        if self.topic_lang_model is None:
            self.topic_lang_model = self._generate_topic_language_model(search_context)


        snip_text = self.__get_snip_text(search_context)

        all_text = topic_text + ' ' + snip_text

        bi_query_generator = BiTermQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
        tri_query_generator = TriTermQueryGeneration(minlen=3, stopwordfile=self._stopword_file)

        tri_query_list = tri_query_generator.extract_queries_from_text(all_text)
        bi_query_list = bi_query_generator.extract_queries_from_text(all_text)

        query_list = tri_query_list + bi_query_list

        query_ranker = QueryRanker(smoothed_language_model=self.topic_lang_model)
        query_ranker.calculate_query_list_probabilities(query_list)
        gen_query_list = query_ranker.get_top_queries(100)

        return gen_query_list


    def update_model(self, search_context):

        if not self.updating:
            return False


        snippet_text = self.__get_snip_text(search_context)


        if snippet_text:
            term_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
            term_extractor.extract_queries_from_text(snippet_text)
            snippet_term_counts = term_extractor.query_count

            topic_text = self.__get_topic_text(search_context)

            document_extractor = SingleQueryGeneration(minlen=3, stopwordfile=self._stopword_file)
            document_extractor.extract_queries_from_text(topic_text)
            document_term_counts = document_extractor.query_count

            title_language_model = LanguageModel(term_dict=document_term_counts)
            background_language_model = LanguageModel(term_dict=snippet_term_counts)
            self.topic_language_model = BayesLanguageModel(title_language_model, background_language_model, beta=10)

            return True
        else:
            return False

    def __get_snip_text(self, search_context):
        document_list = search_context.get_all_examined_snippets()

        # iterate through document_list, pull out relevant snippets / text
        rel_text_list = []
        snippet_text = ''
        for doc in document_list:
            if doc.judgment > 0:
                rel_text_list.append('{0} {1}'.format(doc.title, doc.content))

        if rel_text_list:
            snippet_text = ' '.join(rel_text_list)

        return snippet_text


    def __get_topic_text(self, search_context):
        topic = search_context.topic
        topic_text = topic.title + ' ' + topic.content
        return topic_text