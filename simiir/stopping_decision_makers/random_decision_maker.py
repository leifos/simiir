import random
from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class RandomDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker.
    Given a probability, returns True or False from decide() dependent upon that probability.
    """
    def __init__(self, search_context, logger):
        super(RandomDecisionMaker, self).__init__(search_context, logger)
        self.__probability = 0.25
    
    def decide(self):
        """
        Returns the examine snippet or issue query actions depending on the specified probability.
        """
        if random.random() > self.__probability:
            return Actions.SNIPPET
        
        return Actions.QUERY