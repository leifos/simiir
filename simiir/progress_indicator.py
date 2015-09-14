from progress.bar import Bar
from progress.spinner import Spinner

class ProgressIndicator(object):
    """
    A simple class encapsulating either a progress bar or spinner object.
    """
    def __init__(self, configuration):
        self.__logger = configuration.user.logger
        self.__output_controller = configuration.output
    
    def update(self):
        """
        Sets the progress for the progress indicator.
        """
        state = self.__logger.get_progress()
        
        if hasattr(self, 'indicator'):
            if state is None:
                self.indicator.next()
            else:
                self.indicator.index = state * 100
                self.indicator.next()
        else:
            if state is None:
                self.indicator = Spinner("{0}Simulation executing... ".format(" "*self.__output_controller.output_indentation))
            else:
                self.indicator = Bar("{0}Simulation executing...".format(" "*self.__output_controller.output_indentation), max=100, suffix="%(percent)d%%")