__author__ = 'david'

from ifind.common.query_generation import SingleQueryGeneration
from ifind.common.language_model import LanguageModel
from ifind.common.query_ranker import QueryRanker

def extract_term_dict_from_text(text, stopword_file):
    """
    takes text, parses it, and counts how many times each term occurs.
    :param text: a string
    :return: a dict of {term, count}
    """
    single_term_text_extractor = SingleQueryGeneration(minlen=3, stopwordfile=stopword_file)
    single_term_text_extractor.extract_queries_from_text(text)
    term_counts_dict = single_term_text_extractor.query_count

    return term_counts_dict

def read_in_background(vocab_file):
    """
    Helper method to read in a file containing terms and construct a background language model.
    Returns a LanguageModel instance trained on the vocabulary file passed.
    """
    vocab = {}
    f = open(vocab_file, 'r')

    for line in f:
        tc = line.split(',')
        vocab[tc[0]] = int(tc[1])

    f.close()
    return LanguageModel(term_dict=vocab)

def rank_terms(terms, **kwargs):
    """
    Ranks a list of potential terms by their discriminatory power.
    The length of the list returned == list of initial terms supplied.
    """
    topic_language_model = kwargs.get('topic_language_model', None)

    ranker = QueryRanker(smoothed_language_model=topic_language_model)
    ranker.calculate_query_list_probabilities(terms)
    return ranker.get_top_queries(len(terms))