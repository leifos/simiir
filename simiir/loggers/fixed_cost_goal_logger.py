from loggers import Actions
from loggers.fixed_cost_logger import FixedCostLogger

class FixedCostGoalLogger(FixedCostLogger):
    """
    A simple extension to the FixedCostLogger - considers a search goal, and a hard time limit.
    """
    def __init__(self,
                 output_controller,
                 search_context,
                 time_limit=300,
                 marked_goal=3,
                 query_cost=10,
                 document_cost=20,
                 snippet_cost=3,
                 serp_results_cost=5,
                 mark_document_cost=3):
        """
        Instantiates the BaseLogger class and sets up additional instance variables for the FixedCostLogger.
        """
        self._marked_goal = marked_goal  # How many documents need to be saved before being satisfied?
        
        super(FixedCostGoalLogger, self).__init__(output_controller,
                                                    search_context,
                                                    time_limit,
                                                    query_cost,
                                                    document_cost,
                                                    snippet_cost,
                                                    serp_results_cost,
                                                    mark_document_cost)
    
    def get_progress(self):
        """
        Concrete implementation of the abstract get_progress() method.
        Returns a value between 0 and 1 representing how far through the current simulation the user is.
        """
        return len(self._search_context.get_issued_queries()) / float(len(self._search_context.get_all_queries()))
    
    def is_finished(self):
        """
        Concrete implementation of the is_finished() method from the BaseLogger.
        Returns True if the user hits the goal target, or the hard time limit has been met.
        Or, if there are no queries left in the generated list to issue!
        """
        relevant_count = len(self._search_context.get_relevant_documents())
        
        # Returns true if one of the following two conditions are met:
        #   the marked goal has been reached, or
        #   the time limit/query exhaustion condition (in the base class) has been met.
        return relevant_count >= self._marked_goal or super(FixedCostGoalLogger, self).is_finished()