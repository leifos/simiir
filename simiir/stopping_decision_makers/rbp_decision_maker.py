from random import Random
from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class RBPDecisionMaker(BaseDecisionMaker):
    """
    An implementation of Rank-Biased Precision, operationalised as a stopping strategy. Uses a stochastic roll of the dice to determine
    if a searcher continues or not. Implemented as per Moffat and Zobel (2008).
    """
    def __init__(self, search_context, logger, patience=0.5, base_seed=0):
        """
        Instantiates the decision maker, with a patience factor (defaulting to 0.5).
        The patience factor of RBP determines how patient a searcher is. The closer to 1.0, the deeper the searcher will go.
        """
        super(RBPDecisionMaker, self).__init__(search_context, logger)
        self.__patience = patience
        
        self.__random = Random()
        self.__random.seed(base_seed + 1024)
        
    def decide(self):
        """
        Implements the basic RBP algorithm, using the RBP score computed with the roll of a dice to determine whether
        the searcher continues or not.
        """
        rank = self._search_context.get_current_serp_position()
        rbp_score = self.__patience ** (rank - 1)
        dp = self.__random.random()
        
        if dp > rbp_score:
            return Actions.QUERY
        
        return Actions.SNIPPET