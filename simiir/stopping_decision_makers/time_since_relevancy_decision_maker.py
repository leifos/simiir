from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class TimeSinceRelevancyDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker, implementing the time since encountering a relevant item stopping rule.
    A searcher using this rule will stop a predetermined number of seconds after they last found something relevant, or the start
    of the session if nothing is found that is considered to be relevant.
    """
    def __init__(self, search_context, logger, timeout_threshold=60):
        """
        Instantiates the decision maker, with a timeout threshold parameter (in seconds, defaulting to 60).
        """
        super(TimeSinceRelevancyDecisionMaker, self).__init__(search_context, logger)
        self.__timeout_threshold = timeout_threshold  # This is our threshold; if we reach this value or go above it, we stop.
        self.__last_relevant_time = 0
        self.__last_reported_interaction_time = 0
        
    def decide(self):
        """
        If the searcher reaches timeout_threshold seconds since last considering something relevant (or issuing their query),
        the searcher will abandon the SERP and issue another query, or stop altogether.
        """
        self.__last_relevant_time = self._logger.get_last_marked_time()
        self.__last_interaction_time = self._logger.get_last_interaction_time()
        
        difference = self.__last_interaction_time - self.__last_relevant_time
        
        if difference >= self.__timeout_threshold:
            return Actions.QUERY  # The user has spent enough time on this SERP according to the rule; so bail out.
        
        # We still have time; proceed to examine the next snippet.
        return Actions.SNIPPET