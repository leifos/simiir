import abc
from loggers import Actions

class BaseLogger(object):
    """
    An abstract logger class. Contains the skeleton code and abstract methods to implement a full logger.
    Inherit from this class to create a different logger.
    """
    def __init__(self, output_controller, search_context):
        self._output_controller = output_controller
        self._search_context = search_context
        self._queries_exhausted = False
    
    def log_action(self, action_name, **kwargs):
        """
        A nice helper method which is publicly exposed for logging an event.
        Import loggers.Actions to use the appropriate event type when determining the action.
        Use additional keywords to provide additional arguments to the logger.
        """
        action_mapping = {
            Actions.QUERY  : self._log_query,
            Actions.SERP   : self._log_serp,
            Actions.SNIPPET: self._log_snippet,
            Actions.DOC    : self._log_assess,
            Actions.MARK   : self._log_mark_document,
        }
        
        if action_mapping[action_name]:
            action_mapping[action_name](**kwargs)
        else:
            self.__log_unknown_action(action_name)
    
    @abc.abstractmethod
    def get_last_query_time(self):
        return 0
    
    @abc.abstractmethod
    def get_last_interaction_time(self):
        return 0
    
    @abc.abstractmethod
    def get_last_marked_time(self):
        return 0
    
    @abc.abstractmethod
    def get_last_relevant_snippet_time(self):
        return 0
    
    @abc.abstractmethod
    def get_progress(self):
        """
        Abstract method. Returns a value between 0 and 1 representing the progress of the simulation.
        0 represents the start of the simulation, and 1 represents total completion (e.g. the user's time limit has elapsed.)
        If the progress of the simulation cannot be determined, return None.
        """
        return None
    
    @abc.abstractmethod
    def is_finished(self):
        """
        Abstract method, only returns indication as to whether the list of queries has been exhausted.
        Extend this method to include additional checks to see if the user has reached the limit to what they can do.
        Depending on the implemented logger, this could be the number of queries issued, a time limit, etc...
        """
        return self._queries_exhausted
    
    def queries_exhausted(self):
        """
        This method is called when the list of queries to be issued has been exhausted.
        Sets an internal flag within the Logger, meaning that the next call to .is_finished() will stop the process.
        """
        self._queries_exhausted = True
    
    def _report(self, action, **kwargs):
        """
        A simple method to report the current action being logged.
        Extend this method and call the parent implementation (via super()) to include additional details.
        """
        return "ACTION {0} ".format(action)
    
    @abc.abstractmethod
    def _log_query(self, **kwargs):
        """
        Abstract method. When inheriting from this class, implement this method to appropriately handle a query event.
        Returns None.
        """
        pass
    
    @abc.abstractmethod
    def _log_serp(self, **kwargs):
        """
        Abstract method. When inheriting from this class, implement this method to appropriately handle a SERP examination.
        Returns None.
        """
        pass
    
    @abc.abstractmethod
    def _log_snippet(self, **kwargs):
        """
        Abstract method. When inheriting from this class, implement this method to appropriately handle the examination of a snippet.
        Returns None.
        """
        pass
    
    @abc.abstractmethod
    def _log_assess(self, **kwargs):
        """
        Abstract method. When inheriting from this class, implement this method to appropriately handle assessing a document.
        Returns None.
        """
        pass
    
    @abc.abstractmethod
    def _log_mark_document(self, **kwargs):
        """
        Abstract method. When inheriting from this class, implement this method to appropriately handle the costs of marking a document.
        Returns None.
        """
        pass
    
    def __log_unknown_action(self):
        self._report('UNKNOWN ACTION')