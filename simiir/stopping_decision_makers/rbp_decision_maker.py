from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class RBPDecisionMaker(BaseDecisionMaker):
    """
    A simple, stochastic-based 
    """
    def __init__(self, search_context, logger, patience=0.5):
        """
        Instantiates the decision maker, with a patience factor (defaulting to 0.5).
        The patience factor of RBP determines how patient a searcher is. The closer to 1.0, the deeper the searcher will go.
        """
        super(RBPDecisionMaker, self).__init__(search_context, logger)
        self.__patience = patience
        
    def decide(self):
        """
        Implements the basic RBP algorithm, using the RBP score computed with the roll of a dice to determine whether
        the searcher continues or not.
        """
        return Actions.SNIPPET