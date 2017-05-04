from loggers import Actions
from stopping_decision_makers.satisfaction_decision_maker import SatisfactionDecisionMaker

class TimeLimitedSatisfactionDecisionMaker(SatisfactionDecisionMaker):
    """
    A concrete implementation of a decision maker, implementing a time-limited variant of the satisfaction decision maker
    (extending class SatisfactionDecisionMaker). The satisfaction strategy is used up until the point the timeout threshold is reached;
    at this point, the searcher will give up (out of frustration?) and then issue the next query. This is essentially a failsafe for the
    searcher -- what if they employ this rule, and then find that they cannot find the specified number of documents? They'll waste their
    time on a SERP that is not yielding anything useful.
    """
    def __init__(self, search_context, logger, relevant_threshold=3, timeout_threshold=20):
        """
        Instantiates the decision maker, using a default relevant threshold of 3.
        """
        super(TimeLimitedSatisfactionDecisionMaker, self).__init__(search_context, logger, relevant_threshold)
        self.__timeout_threshold = timeout_threshold  # The timeout threshold; abandon the SERP once this has been reached.
    
    def decide(self):
        """
        If the searcher has examined a given number of snippets judged to be relevant, then we abandon the search and issue another query.
        Otherwise, we keep going until we find the required number of items (defined by self.__relevant_threshold).
        """
        last_query_time = self._logger.get_last_query_time()
        last_interaction_time = self._logger.get_last_interaction_time()
        
        difference = last_interaction_time - last_query_time
        
        if difference >= self.__timeout_threshold:
            # If this condition has been met, we are still on the SERP, looking for content.
            # However, we've had enough; we've timed out, and thus we move to the next query regardless of whether we have met
            # the satisfaction rule criterion.
            return Actions.QUERY  # The user has spent enough time on this SERP according to the rule; so bail out.
        
        # If the timeout threshold has not elapsed, then we fall back to the satisfaction decision maker's judgement.
        return super(TimeLimitedSatisfactionDecisionMaker, self).decide()