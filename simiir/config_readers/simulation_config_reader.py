from itertools import product
from config_readers import ConfigReaderError
from config_readers.base_config_reader import BaseConfigReader
from config_readers import parse_boolean, empty_string_check, filesystem_exists_check, check_attributes

class SimulationConfigReader(BaseConfigReader):
    """
    The Simulation Configuration reader - checks for validity in the supplied settings, and creates a series of components for use with the simulations.
    This includes a UserConfigReader - which in turn contains components relevant to a simulated user.
    """
    def __init__(self, config_filename=None):
        super(SimulationConfigReader, self).__init__(config_filename=config_filename, dtd_filename='simulation.dtd')
        
        # Specify the options which do not change over an interation, and those which do.
        self.__static = ['output', 'searchInterface']
        self.__iterables = ['topics', 'users']
        
        self.__calculate_iterations()
    
    def __iter__(self):
        """
        Turns the Configuration Reader into an iterator; allowing one to iterate through all the different configuration combinations.
        """
        return self
    
    def get_base_dir(self):
        """
        Returns the base directory for the simulations as a string.
        """
        return self._config_dict['output']['@baseDirectory']
    
    def next(self):
        """
        Acts as an interator - returns the next set of components for next iteration of the simulation.
        A StopIteration exception is raised if no further configuration iterations are available.
        """
        def get_next_configuration():
            """
            Returns the next configuration set from the configuration file.
            If no further configuration sets are available, None is returned.
            """
            iteration_config = self.__iterables[self.__iterables_counter]

            for static_option in self.__static:
                if static_option not in self._config_dict:
                    raise ConfigReaderError("Simulation configuration option '{0}' not found. Please check the SimulationConfigReader class for typos.".format(static_option))

                iteration_config[static_option] = self._config_dict[static_option]

            return iteration_config
        
        if self.__iterables_counter >= len(self.__iterables):
            raise StopIteration  # No more iterations available!
        
        components = {}
        configuration_set = get_next_configuration()
        
        from component_generators.simulation_generator import SimulationComponentGenerator
        bg = SimulationComponentGenerator(self._config_dict['@id'], configuration_set)
        
        #print bg
        
        self.__iterables_counter = self.__iterables_counter + 1
        return bg
    
    def __calculate_iterations(self):
        """
        Returns a list of the objects which are to be traversed through, making all the different possible combinations of simulations to run.
        """
        iterables = {}
        
        def get_type(type_options):
            key = self._config_dict[type_options].keys()[0]
            data = self._config_dict[type_options][key]
            
            if type(data) == dict:
                iterables[key] = [data]
            else:
                iterables[key] = data
        
        for config_type in self.__iterables:
            get_type(config_type)
        
        self.__iterables = [dict(zip(iterables, v)) for v in product(*iterables.values())]  # Calculates the cartesian product of all the lists to iterate to generate permutations.
        self.__iterables_counter = 0
    
    def _validate_config(self):
        """
        Validates the contents of the configuration file - under the assumption that it is well formed and conforms to the DTD.
        Checks aspects such as the types of attributes, for example.
        """
        # Simulation ID
        empty_string_check(self._config_dict['@id'])
        
        # Output
        empty_string_check(self._config_dict['output']['@baseDirectory'])
        self._config_dict['output']['@saveInteractionLog'] = parse_boolean(self._config_dict['output']['@saveInteractionLog'])
        self._config_dict['output']['@saveRelevanceJudgments'] = parse_boolean(self._config_dict['output']['@saveRelevanceJudgments'])
        self._config_dict['output']['@trec_eval'] = parse_boolean(self._config_dict['output']['@trec_eval'])
        
        # Topics
        def check_topic(t):
            """
            Checks a given topic, t. Looks for a topic ID and a valid topic description file.
            """
            empty_string_check(t['@id'])
            filesystem_exists_check(t['@filename'])
            filesystem_exists_check(t['@qrelsFilename'])
            
        topics = self._config_dict['topics']['topic']
        
        if type(topics) == list:
            for topic in topics:
                check_topic(topic)
        else:
            check_topic(topics)
        
        # Users
        users = self._config_dict['users']['user']
        
        if type(users) == list:
            for user in users:
                filesystem_exists_check(user['@configurationFile'])
        else:
            filesystem_exists_check(users['@configurationFile'])
        
        # Search Interface
        empty_string_check(self._config_dict['searchInterface']['@class'])
        check_attributes(self._config_dict['searchInterface'])