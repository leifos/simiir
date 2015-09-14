import abc

class BaseDecisionMaker(object):
    """
    
    """
    def __init__(self, search_context):
        self._search_context = search_context
    
    @abc.abstractmethod
    def decide(self):
        """
        Abstract method - must be implemented by an inheriting class.
        Returns an action - from the loggers.Actions enum.
        """
        pass