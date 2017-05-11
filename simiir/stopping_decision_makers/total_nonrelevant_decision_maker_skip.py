from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class TotalNonrelDecisionMakerSkip(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker.
    Returns True iif the depth at which a user is in a SERP is less than a predetermined value.
    
    If a snippet has been encountered which has been previously examined, then the snippet does not count towards the nonrelevant total.
    """
    def __init__(self, search_context, logger, nonrelevant_threshold=3):
        super(TotalNonrelDecisionMakerSkip, self).__init__(search_context, logger)
        self.__nonrelevant_threshold = nonrelevant_threshold  # The threshold; get to this point, we stop in the current SERP.

    def decide(self):
        """
        If the user's current position in the current SERP is < the maximum depth, look at the next snippet in the SERP.
        Otherwise, a new query should be issued.
        """
        counter = 0
        examined_snippets = self._search_context.get_examined_snippets()
        previous = []
        
        for snippet in examined_snippets:
            judgment = snippet.judgment
            
            if judgment == 0:
                if self.__get_previous_judgment(previous, snippet) != 0:
                    counter = counter + 1
                    
                    if counter == self.__nonrelevant_threshold:
                        return Actions.QUERY
            
            # Add the snippet to our list of previously examined snippets.
            previous.append(snippet)
            
        # If we get here, we are okay - so we examine the next snippet.
        return Actions.SNIPPET
    
    def __get_previous_judgment(self, previously_seen, snippet):
        """
        Looking through the list of previously examined snippets, returns the judgment for that snippet.
        If the snippet has not been seen before, -1 is returned.
        """
        for previous_snippet in previously_seen:
            if previous_snippet.doc_id == snippet.doc_id:
                return previous_snippet.judgment
        
        return -1