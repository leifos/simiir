from random import Random
from loggers import Actions
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class INSTDecisionMaker(BaseDecisionMaker):
    """
    A decision maker implementing the INST metric.
    Equations from Moffat et al. (ADCS 2015)
    """
    def __init__(self, search_context, logger, t=5, base_seed=0):
        """
        Instantiates the decision maker, with a T (expected documents to find) value of 5.
        """
        super(INSTDecisionMaker, self).__init__(search_context, logger)
        self.__t = t
        
        self.__random = Random()
        self.__random.seed(base_seed + 1024)
        
    def decide(self):
        """
        Implements INST. Given the positional weightings (W), we can, with a roll of the dice, decide whether the searcher
        should continue examining the SERP, or stop and abandon it.
        """
        examined_snippets = self._search_context.get_examined_snippets()
        rank = len(examined_snippets) # Assumption here that the rank is == to the number of snippets examined.
        
        r_i = self.__calculate_R_i(rank, examined_snippets)
        t_i = self.__calculate_T_i(r_i)
        w_i = self.__calculate_W(rank, t_i)
        
        if rank == 1:
            w_1 = w_i
        else:
            w_1 = self.__calculate_W1(examined_snippets)
        
        dp = self.__random.random()
        
        if dp > (w_i / w_1):
            return Actions.QUERY
        
        return Actions.SNIPPET
    
    def __calculate_R_i(self, rank, judgements):
        cg = 0
    
        for i in range(0, rank):
            judgement = judgements[i].judgment
            
            if judgement < 0:  # Assume unjudged content is not relevant (as per TREC)
                judgement = 0
            
            cg = cg + judgement
    
        return cg
    
    def __calculate_T_i(self, R_i):
        return self.__t - R_i
    
    def __calculate_W(self, rank, T_i):
        return 1.0 / (rank + self.__t + T_i)**2
    
    def __calculate_W1(self, judgements):
        r_1 = self.__calculate_R_i(1, judgements)
        t_1 = self.__calculate_T_i(r_1)
        w_1 = self.__calculate_W(1, t_1)
        
        return w_1