from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class TimeSinceRelevancyDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker, implementing the time since encountering a relevant item stopping rule.
    A searcher using this rule will stop a predetermined number of seconds after they last found something relevant, or the start
    of the session if nothing is found that is considered to be relevant.
    """
    def __init__(self, search_context, logger, timeout_threshold=60, on_mark=True):
        """
        Instantiates the decision maker, with a timeout threshold parameter (in seconds, defaulting to 60).
        The parameter on_mark dictates what event the stopping strategy should consider as a "relevant" event happening.
        If set to True, the strategy considers when a document is marked as relevant as the "relevant" event.
        If set to False, the strategy considers when a snippet is considered as attractive as the "relevant" event.
        """
        super(TimeSinceRelevancyDecisionMaker, self).__init__(search_context, logger)
        self.__timeout_threshold = timeout_threshold  # This is our threshold; if we reach this value or go above it, we stop.
        self.__on_mark = on_mark
        
    def decide(self):
        """
        If the searcher reaches timeout_threshold seconds since last considering something relevant (or issuing their query),
        the searcher will abandon the SERP and issue another query, or stop altogether.
        """
        if self.__on_mark:
            last_relevant_time = self._logger.get_last_marked_time()
        else:
            last_relevant_time = self._logger.get_last_relevant_snippet_time()
        
        last_interaction_time = self._logger.get_last_interaction_time()
        
        difference = last_interaction_time - last_relevant_time
        
        if difference >= self.__timeout_threshold:
            return Actions.QUERY  # The user has spent enough time on this SERP according to the rule; so bail out.
        
        # We still have time; proceed to examine the next snippet.
        return Actions.SNIPPET