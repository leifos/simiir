from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker
from stopping_decision_makers.total_nonrelevant_decision_maker import TotalNonrelDecisionMaker
from stopping_decision_makers.time_limited_satisfaction_decision_maker import TimeLimitedSatisfactionDecisionMaker

class SatisfactionFrustrationCombinationDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker, implementing a combination of the frustration and satisfaction heuristics.
    If one says move to the next query, then abandon the query!
    """
    def __init__(self, search_context, logger, relevant_threshold=3, nonrelevant_threshold=3, timeout_threshold=20):
        """
        Instantiates the decision maker.
        """
        super(SatisfactionFrustrationCombinationDecisionMaker, self).__init__(search_context, logger)
        self.__relevant_threshold = relevant_threshold
        self.__nonrelevant_threshold = nonrelevant_threshold
        self.__timeout_threshold = timeout_threshold
        
        self.__frustration = TotalNonrelDecisionMaker(search_context=search_context,
                                                      logger=logger,
                                                      nonrelevant_threshold=self.__nonrelevant_threshold)
        
        self.__satisfaction = TimeLimitedSatisfactionDecisionMaker(search_context=search_context,
                                                                   logger=logger,
                                                                   relevant_threshold=self.__relevant_threshold,
                                                                   timeout_threshold=self.__timeout_threshold)
    
    def decide(self):
        """
        If one says query, then the searcher will abandon the query and reformulate.
        """
        frustration_decision = self.__frustration.decide()
        satisfaction_decision = self.__satisfaction.decide()
        
        if frustration_decision == Actions.QUERY or satisfaction_decision == Actions.QUERY:
            return Actions.QUERY
        
        return Actions.SNIPPET