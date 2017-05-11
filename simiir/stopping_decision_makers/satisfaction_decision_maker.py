from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class SatisfactionDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker, implementing the satisfaction/count stopping rules.
    Instructs a searcher to stop iif the searcher has found a predetermined number of snippets judged to be relevant.
    """
    def __init__(self, search_context, logger, relevant_threshold=3):
        """
        Instantiates the decision maker, using a default relevant threshold of 3.
        """
        super(SatisfactionDecisionMaker, self).__init__(search_context, logger)
        self.__relevant_threshold = relevant_threshold  # The threshold; get to this point, and we abandon the SERP.
    
    def decide(self):
        """
        If the searcher has examined a given number of snippets judged to be relevant, then we abandon the search and issue another query.
        Otherwise, we keep going until we find the required number of items (defined by self.__relevant_threshold).
        """
        counter = 0
        examined_snippets = self._search_context.get_examined_snippets()
        
        for snippet in examined_snippets:
            judgement = snippet.judgment
            
            if judgement > 0:
                counter = counter + 1  # Found a relevant item; increment the counter.
                
                if counter == self.__relevant_threshold:  # If the counter is reached, abandon the SERP.
                    return Actions.QUERY
        
        # If we get here, we need to keep looking.
        return Actions.SNIPPET