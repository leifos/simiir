from loggers import Actions
from serp_impressions import PatchTypes
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker
from stopping_decision_makers.time_since_relevancy_decision_maker import TimeSinceRelevancyDecisionMaker
from stopping_decision_makers.limited_satisfaction_decision_maker import LimitedSatisfactionDecisionMaker

class PatchCombinationDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker, considering the "single patch type" findings by McNair (1982), from Foraging Theory
    (Stephens and Krebs, 1986, Section 8.3). This stopping strategy is essentially a proxy -- depending upon the how the patch (or SERP)
    has been judged by the searcher (through the SERP impression module), a different stopping strategy is employed.
    
    For a patch judged to yield high gain early on, we employ the limited satisfaction rule (LimitedSatisfactionDecisionMaker).
    Otherwise, for a patch that depresses gradually, we employ the giving up time-based rule (TimeSinceRelevancyDecisionMaker).
    
    If the patch has not been judged, this stopping strategy raises an exception as we cannot deduce what strategy to employ.
    
    The limited satisfaction rule is added by us; it inherently makes sense to do so in case the judging of the SERP
    initially proves to be incorrect, and it's hard to find a certain number of relevant items -- the user will abandon after two pages of rubbish.
    """
    def __init__(self, search_context, logger, relevant_threshold=3, timeout_threshold=60, on_mark=True, serp_size=10, nonrelevant_threshold=10):
        """
        Instantiates the combination foraging theory decision maker.
        Requires parameters from both the TimeLimitedSatisfactionDecisionMaker and TimeSinceRelevancyDecisionMaker strategies.
        """
        super(PatchCombinationDecisionMaker, self).__init__(search_context, logger)
        self.__relevant_threshold = relevant_threshold
        self.__timeout_threshold = timeout_threshold
        self.__serp_size = serp_size
        self.__on_mark = on_mark
        self.__nonrelevant_threshold = nonrelevant_threshold
        
        self.__last_patch_type = None  # What was the last patch type? We record this so we change the strategy as required.
        self.__strategy = None  # Represents a reference to the stopping strategy that is chosen to be used.
        
    def decide(self):
        """
        Returns the next action based upon the currently active stopping strategy (self.__strategy).
        Strategies are actively switched according to the patch judgement (decided in the SERP Impression component).
        """
        self.__check_strategy()
        return self.__strategy.decide()
    
    def __check_strategy(self):
        """
        Checks the currently deployed stopping strategy (e.g. self.__strategy) against the patch type.
        If they don't match, the strategy is switched to the strategy that should work best for the given patch.
        """
        patch_mappings = {
            PatchTypes.EARLY_GAIN       : self.__set_satisfaction,
            PatchTypes.GRADUAL_INCREASE : self.__set_time_limited,
            PatchTypes.UNDEFINED        : self.__set_undefined,
        }
        
        judged_patch_type = self._search_context.get_last_patch_type()
        
        if judged_patch_type is None:
            raise ValueError("No SERP has been yet examined. This exception shouldn't really happen.")
        
        # If the patch type currently doesn't match what we were looking at previously, switch the stopping strategy.
        if judged_patch_type != self.__last_patch_type:
            patch_mappings[judged_patch_type]()  # Set up the decision maker as per the patch type judgement.
            self.__last_patch_type = judged_patch_type
    
    def __set_satisfaction(self):
        """
        Sets the stopping strategy to the satisfaction stopping strategy.
        """
        self.__strategy = LimitedSatisfactionDecisionMaker(search_context=self._search_context,
                                                           logger=self._logger,
                                                           relevant_threshold=self.__relevant_threshold,
                                                           serp_size=self.__serp_size,
                                                           nonrelevant_threshold=self.__nonrelevant_threshold,
                                                           consider_documents=self.__on_mark)
    
    def __set_time_limited(self):
        """
        Sets the stopping strategy to a time-based frustration rule (since last seen relevancy).
        """
        self.__strategy = TimeSinceRelevancyDecisionMaker(search_context=self._search_context,
                                                          logger=self._logger,
                                                          timeout_threshold=self.__timeout_threshold,
                                                          on_mark=self.__on_mark)
    
    def __set_undefined(self):
        """
        If the patch is not defined, we raise an exception. We need to know the patch type to allocate a stopping strategy.
        If this is reached, the SERP Impression component needs to be able to actively judge snippets (and thus the SERP 'patch').
        """
        raise ValueError("To use the PatchCombinationDecisionMaker, you must use a SERP Impression component that judges the SERP patch type.")