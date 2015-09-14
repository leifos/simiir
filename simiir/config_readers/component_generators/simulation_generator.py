import os
from search_interfaces import Topic
from output_controller import OutputController
from config_readers.user_config_reader import UserConfigReader
from config_readers.component_generators.base_generator import BaseComponentGenerator

class SimulationComponentGenerator(BaseComponentGenerator):
    """
    A component generator for Simulations. Extends the BaseComponentGenerator.
    Includes a reference to a UserComponentGenerator, containing all user-relevant components.
    """
    def __init__(self, simulation_id, config_dict):
        """
        Instantiates all the necessary components for the given configuration dictionary.
        """
        super(SimulationComponentGenerator, self).__init__(config_dict)
        
        # What is the simulation's ID?
        self.simulation_id = simulation_id
        
        # Create an OutputController object to handle the saving of output files to disk.
        self.output = OutputController(self, self._config_dict['output'])
        
        # Generate a Topic object.
        self.topic = self.__generate_topic()
        
        # Generate the search interface to be used.
        self.search_interface = self._get_object_reference(config_details=self._config_dict['searchInterface'],
                                                           package='search_interfaces')
        
        # Create the user object - by loading the specified file into a UserConfigReader, then obtaining its components.
        user_config_file = self._config_dict['user']['@configurationFile']
        self.user = UserConfigReader(user_config_file).get_component_generator(self)
        
        # Creates a "base ID" for the saving of files, comprised of different component IDs (to uniquely identify the simulation).
        self.base_id = '{0}-{1}-{2}'.format(self.simulation_id, self.topic.id, self.user.id)
    
    def prettify(self):
        """
        Returns a prettified string representation with the key configuration details for the simulation.
        """
        return_string = "{0}Topic: {1}{2}".format(" "*self.output.output_indentation*2, self.topic.id, os.linesep)
        return_string = "{0}{1}{2}".format(return_string, "{0}Search Interface: {1}{2}{3}".format(" "*self.output.output_indentation*2, self._config_dict['searchInterface']['@class'], os.linesep, self._prettify_attributes(self._config_dict['searchInterface'], self.output.output_indentation)), os.linesep)
        
        return return_string
        
    def __generate_topic(self):
        """
        Generates a topic object based on the settings in the configuration dictionary provided.
        """
        config = self._config_dict['topic']
        
        topic = Topic(config['@id'], qrels_filename=config['@qrelsFilename'])
        topic.read_topic_from_file(config['@filename'])
        
        return topic