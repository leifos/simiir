from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class TotalNonrelDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker.
    Returns True iif the depth at which a user is in a SERP is less than a predetermined value.
    """
    def __init__(self, search_context, logger, nonrelevant_threshold=3):
        super(TotalNonrelDecisionMaker, self).__init__(search_context, logger)
        self.__nonrelevant_threshold = nonrelevant_threshold  # The threshold; get to this point, we stop in the current SERP.

    def decide(self):
        """
        If the user's current position in the current SERP is < the maximum depth, look at the next snippet in the SERP.
        Otherwise, a new query should be issued.
        """
        counter = 0
        examined_snippets = self._search_context.get_examined_snippets()
        
        # If the judgment for a snippet is -1, then it was seen previously and was therefore not judged - so we should skip it.
        
        for snippet in examined_snippets:
            judgment = snippet.judgment
            
            if judgment == 0:
                counter = counter + 1  # Found something nonrelevant; increment counter

                if counter == self.__nonrelevant_threshold:
                    return Actions.QUERY

        # If we get here, we are okay - so we examine the next snippet.
        return Actions.SNIPPET