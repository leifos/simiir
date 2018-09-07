from loggers import Actions
from serp_impressions import PatchTypes
from simiir.utils.data_handlers import get_data_handler
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker
from stopping_decision_makers.time_since_relevancy_decision_maker import TimeSinceRelevancyDecisionMaker
from stopping_decision_makers.limited_satisfaction_decision_maker import LimitedSatisfactionDecisionMaker

class PatchCombinationSimplifiedDecisionMaker(BaseDecisionMaker):
    
    
    def __init__(self, search_context, logger, relevant_threshold=3, timeout_threshold=60, on_mark=True, serp_size=10, nonrelevant_threshold=10, qrel_file=None):
        super(PatchCombinationSimplifiedDecisionMaker, self).__init__(search_context, logger)
        self.__relevant_threshold = relevant_threshold
        self.__timeout_threshold = timeout_threshold
        self.__serp_size = serp_size
        self.__on_mark = on_mark
        self.__nonrelevant_threshold = nonrelevant_threshold
        self.__qrels = get_data_handler(filename=qrel_file)
        
        self.__last_patch_type = None  # What was the last patch type? We record this so we change the strategy as required.
        self.__strategy = None  # Represents a reference to the stopping strategy that is chosen to be used.
    
    
    def decide(self):
        """
        Decides.
        """
        topic_id = self._search_context.topic.id
        first_doc_id = self._search_context.get_current_results()[0].docid
        
        first_judgement = self.__qrels.get_value_fallback(topic_id, first_doc_id)
        
        if self.__relevant_threshold == 0:
            self.__set_time_limited()
        else:
            if first_judgement > 0:
                self.__set_satisfaction()
            else:
                self.__set_time_limited()
        
        return self.__strategy.decide()
    
    
    def __set_satisfaction(self):
        """
        Sets the stopping strategy to the satisfaction stopping strategy.
        """
        self.__strategy = LimitedSatisfactionDecisionMaker(search_context=self._search_context,
                                                           logger=self._logger,
                                                           relevant_threshold=self.__relevant_threshold,
                                                           serp_size=self.__serp_size,
                                                           nonrelevant_threshold=self.__nonrelevant_threshold,
                                                           consider_documents=not self.__on_mark)
    
    
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