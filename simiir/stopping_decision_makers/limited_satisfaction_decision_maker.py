from loggers import Actions
from stopping_decision_makers.satisfaction_decision_maker import SatisfactionDecisionMaker

class LimitedSatisfactionDecisionMaker(SatisfactionDecisionMaker):
    """
    An extension to the SatisfactionDecisionMaker. This stopping strategy employs the same basic rule (stop after
    finding x relevant items), but includes a fallback condition to stop a searcher from wasting time if they end up
    on a poor quality SERP, and would be stuck examining it until the time limit expires.
    
    This is achieved by the following. The satisfaction condition is followed, unless:
        - not a single item has been considered relevant in the first SERP page (set by serp_size); or
        - if nonrelevant_threshold non-relevant items have been seen since the last relevant item.
    The second rule is essentially the frustration rule -- give up after you've not seen anything relevant.
    
    If either of these conditions are met, this stopping strategy override the satisfaction rule and the searcher
    abandons the SERP. You can differentiate between what should be considered relevant (i.e. documents or snippets)
    with the consider_documents boolean switch.
    """
    def __init__(self, search_context, logger, relevant_threshold=3, serp_size=10, nonrelevant_threshold=10, consider_documents=True):
        """
        Instantiates the decision maker, using a default relevant threshold of 3, a SERP size of 10 and a
        nonrelevant threshold of 10 (equivalent of one page of the SERP).
        """
        super(LimitedSatisfactionDecisionMaker, self).__init__(search_context, logger, relevant_threshold=relevant_threshold)
        self.__relevant_threshold = relevant_threshold  # The threshold; get to this point, and we abandon the SERP.
        self.__serp_size = serp_size
        self.__nonrelevant_threshold = nonrelevant_threshold
        self.__consider_documents = consider_documents
    
    def decide(self):
        """
        Apply the rules as defined in the class description.
        """
        satisfaction_decision = super(LimitedSatisfactionDecisionMaker, self).decide()
        serp_position = self._search_context.get_current_serp_position()
        relevant_count = self.__get_relevant_count()
        last_relevant_rank = self.__get_last_relevant_rank()
        
        # If we are on the first SERP page, return the satisfaction decision.
        if serp_position < self.__serp_size:
            return satisfaction_decision
        # If by the end of the first SERP we have not found anything, we stop.
        if serp_position == self.__serp_size and relevant_count == 0:
            return Actions.QUERY
        # After the first SERP has been examined, switch back to a "frustration rule".
        elif serp_position - last_relevant_rank == self.__nonrelevant_threshold:
            return Actions.QUERY
        
        return satisfaction_decision
    
    def __get_relevant_count(self):
        """
        Returns a count of the number of snippets/documents that have been judged relevant for the current query.
        """
        count = 0
        
        if self.__consider_documents:
            items = self._search_context.get_examined_documents()
        else:
            items = self._search_context.get_examined_snippets()
        
        for item in items:
            if item.judgment > 0:
                count = count + 1
        
        return count
    
    def __get_last_relevant_rank(self):
        """
        What was the rank of the last snippet/document considered relevant?
        If no documents have been marked, 0 is returned.
        """
        serp_order = self._search_context.get_current_results()
        last_rank = 0
        rank = 1
        
        if self.__consider_documents:
            items = self._search_context.get_examined_documents()
        else:
            items = self._search_context.get_examined_snippets()
        
        for item in items:
            item_doc_id = item.doc_id
            item_rank = 0
            i = 1
            
            for res in serp_order:
                if res.docid == item_doc_id:
                    item_rank = i
                
                i = i + 1
            
            if item.judgment > 0:
                last_rank = item_rank
        
        return last_rank