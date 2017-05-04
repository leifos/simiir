from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class TimeDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker, implementing the time based stopping rule.
    A searcher using this rule will stop after a predetermined number of seconds have elapsed since they issued a query.
    """
    def __init__(self, search_context, logger, timeout_threshold=60):
        """
        Instantiates the decision maker, with a timeout threshold parameter (in seconds, defaulting to 60).
        """
        super(TimeDecisionMaker, self).__init__(search_context, logger)
        self.__timeout_threshold = timeout_threshold  # This is our threshold; if we reach this value or go above it, we stop.
        
    def decide(self):
        """
        If the searcher reaches timeout_threshold seconds since issuing their query, the searcher will abandon the SERP,
        and issue another query, or stop altogether.
        """
        last_query_time = self._logger.get_last_query_time()
        last_interaction_time = self._logger.get_last_interaction_time()
        
        difference = last_interaction_time - last_query_time
        
        if difference >= self.__timeout_threshold:
            return Actions.QUERY  # The user has spent enough time on this SERP according to the rule; so bail out.
        
        # We still have time; proceed to examine the next snippet.
        return Actions.SNIPPET