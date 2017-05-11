__author__ = 'leif'
from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker
import logging

log = logging.getLogger('decsion_makers.ift_based_decision_makers')


class IftBasedDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker.
    If current rank is less tha the rank threshold, returns Actions.SNIPPET
    Returns Actions.QUERY if the average gain of the current rank is not equal to or greater than the threshold,
    else it returns Actions.SNIPPET
    """

    def __init__(self, search_context, logger, gain_threshold=0.015, query_time=15.0, doc_time=20.0,discount=0.5, rank_threshold=1):
        super(IftBasedDecisionMaker, self).__init__(search_context, logger)
        self.__rank_threshold = rank_threshold  # Before basing the decision on the gain recieved, examine this many documents first
        self.__gain_threshold = gain_threshold  # average gain per second
        # The after rate of gain, if the current rate of gain does not exceed this... STOP
        self.__query_time = query_time
        self.__doc_time = doc_time
        self.__discount = discount # how much the gain a ranks is discounted
        
    def decide(self):
        """
        First checks to see if the rank threshold is exceeded, i.e. have they seen enough to make an estimate of the gain
        if so, then, is the current rate of gain greater than or equal to the average rate of gain, if so SNIPPET, else QUERY
        """
        if self._search_context.get_current_serp_position() <  self.__rank_threshold:
            return Actions.SNIPPET
        
        dis_cum_gain = 0.0
        pos = 0.0
        examined_snippets = self._search_context.get_examined_snippets()
        
        for snippet in examined_snippets:
            pos = pos + 1.0
            j = float(snippet.judgment)
            if j <0:
                j = 0
            dis_cum_gain += (j)*(1.0/(pos**self.__discount))

        #The average rate of gain, ie. gain per second
        total_time = (float(self.__query_time) + (float(self.__doc_time)*pos))
        avg_dis_cum_gain = dis_cum_gain / total_time

        log.debug("IFT1: q: {0} pos: {1} gps: {2}, {3}, {4}".format(self._search_context.get_last_query().terms, pos, avg_dis_cum_gain, dis_cum_gain, total_time))

        if avg_dis_cum_gain >= self.__gain_threshold:
            return Actions.SNIPPET
        return Actions.QUERY
        
class Ift2BasedDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker.
    If current rank is less tha the rank threshold, returns Actions.SNIPPET
    Returns Actions.QUERY if the average gain of the current rank is not equal to or greater than the threshold,
    else it returns Actions.SNIPPET
    """

    def __init__(self, search_context, gain_threshold=0.015, query_time=15.0, doc_time=20.0, snip_time=3.0, discount=0.5, rank_threshold=1):
        super(Ift2BasedDecisionMaker, self).__init__(search_context)
        self.__rank_threshold = rank_threshold  # Before basing the decision on the gain recieved, examine this many documents first
        self.__gain_threshold = gain_threshold  # average gain per second
        # The after rate of gain, if the current rate of gain does not exceed this... STOP
        self.__query_time = query_time
        self.__doc_time = doc_time
        self.__snip_time = snip_time
        self.__discount = discount # how much the gain a ranks is discounted



    def decide(self):
        """
        First checks to see if the rank threshold is exceeded, i.e. have they seen enough to make an estimate of the gain
        if so, then, is the current rate of gain greater than or equal to the average rate of gain, if so SNIPPET, else QUERY

        """

        if self._search_context.get_current_serp_position() <  self.__rank_threshold:
            return Actions.SNIPPET


        dis_cum_gain = 0.0
        pos = 0.0
        examined_snippets = self._search_context.get_examined_snippets()
        examined_docs = self._search_context.get_examined_documents()
        for doc in examined_docs:
            pos = pos + 1.0
            j = float(doc.judgment)
            if j <0:
                j = 0
            dis_cum_gain += (j)*(1.0/(pos**self.__discount))

        #The average rate of gain, ie. gain per second
        ns = float(len(examined_snippets))
        nd = float(len(examined_docs))

        total_time = self.__query_time + (nd * self.__doc_time) +(ns * self.__snip_time )
        avg_dis_cum_gain = dis_cum_gain / total_time

        log.debug("IFT2: q: {0} pos: {1} gps: {2}, {3}, {4}".format(self._search_context.get_last_query().terms, pos, avg_dis_cum_gain, dis_cum_gain, total_time))

        if avg_dis_cum_gain >= self.__gain_threshold:
            return Actions.SNIPPET
        return Actions.QUERY

