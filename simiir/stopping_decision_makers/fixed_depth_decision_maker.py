from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class FixedDepthDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker.
    Returns True iif the depth at which a user is in a SERP is less than a predetermined value.
    """
    def __init__(self, search_context, logger, depth):
        super(FixedDepthDecisionMaker, self).__init__(search_context, logger)
        self.__depth = depth
    
    def decide(self):
        """
        If the user's current position in the current SERP is < the maximum depth, look at the next snippet in the SERP.
        Otherwise, a new query should be issued.
        """
        if self._search_context.get_current_serp_position() < self.__depth:
            return Actions.SNIPPET
        
        return Actions.QUERY