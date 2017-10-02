import os
#from search_context import SearchContext
from config_readers.component_generators.base_generator import BaseComponentGenerator

class UserComponentGenerator(BaseComponentGenerator):
    """
    """
    def __init__(self, simulation_components, config_dict):
        super(UserComponentGenerator, self).__init__(config_dict)
        
        self.__simulation_components = simulation_components
        
        
        # Store the user's ID for easy access.
        self.id = self._config_dict['@id']
        
        # Create the user's query generator.
        self.query_generator = self._get_object_reference(config_details=self._config_dict['queryGenerator'],
                                                          package='query_generators',
                                                          components=[])
        
        # Create the search context object.
        # self.search_context = self.__generate_search_context()  # When we had only a single search context class.
        self.search_context = self._get_object_reference(config_details=self._config_dict['searchContext'],
                                                         package='search_contexts',
                                                         components=[('search_interface', self.__simulation_components.search_interface),
                                                                     ('output_controller', self.__simulation_components.output),
                                                                     ('topic', self.__simulation_components.topic),
                                                                    ])
        
        # Create the user's snippet classifier.
        self.snippet_classifier = self._get_object_reference(config_details=self._config_dict['textClassifiers']['snippetClassifier'],
                                                             package='text_classifiers',
                                                             components=[('topic', self.__simulation_components.topic),
                                                                         ('search_context', self.search_context)])
        
        # Create the uer's document classifier.
        self.document_classifier = self._get_object_reference(config_details=self._config_dict['textClassifiers']['documentClassifier'],
                                                              package='text_classifiers',
                                                              components=[('topic', self.__simulation_components.topic),
                                                                          ('search_context', self.search_context)])
        
        # Generate the logger object for the simulation.
        self.logger = self._get_object_reference(config_details=self._config_dict['logger'],
                                                         package='loggers',
                                                         components=[('output_controller', self.__simulation_components.output),
                                                                     ('search_context', self.search_context)])
        
        # Create the decision maker (judging relevancy).
        self.decision_maker = self._get_object_reference(config_details=self._config_dict['stoppingDecisionMaker'],
                                                         package='stopping_decision_makers',
                                                         components=[('search_context', self.search_context),
                                                                     ('logger', self.logger)])
        
        # Create the SERP impression component (used for some more advanced stopping models).
        self.serp_impression = self._get_object_reference(config_details=self._config_dict['serpImpression'],
                                                          package='serp_impressions',
                                                          components=[('search_context', self.search_context)])
    
    def prettify(self):
        """
        Returns a prettified string representation with the key configuration details for the simulation.
        """
        return_string = "{0}{1}".format("{0}Query Generator: {1}{2}{3}".format(" "*self.__simulation_components.output.output_indentation*2, self._config_dict['queryGenerator']['@class'], os.linesep, self._prettify_attributes(self._config_dict['queryGenerator'], self.__simulation_components.output.output_indentation)), os.linesep)
        return_string = "{0}{1}{2}".format(return_string, "{0}Snippet Classifier: {1}{2}{3}".format(" "*self.__simulation_components.output.output_indentation*2, self._config_dict['textClassifiers']['snippetClassifier']['@class'], os.linesep, self._prettify_attributes(self._config_dict['textClassifiers']['snippetClassifier'], self.__simulation_components.output.output_indentation)), os.linesep)
        return_string = "{0}{1}{2}".format(return_string, "{0}Document Classifier: {1}{2}{3}".format(" "*self.__simulation_components.output.output_indentation*2, self._config_dict['textClassifiers']['documentClassifier']['@class'], os.linesep, self._prettify_attributes(self._config_dict['textClassifiers']['documentClassifier'], self.__simulation_components.output.output_indentation)), os.linesep)
        return_string = "{0}{1}{2}".format(return_string, "{0}Stopping Decision Maker: {1}{2}{3}".format(" "*self.__simulation_components.output.output_indentation*2, self._config_dict['stoppingDecisionMaker']['@class'], os.linesep, self._prettify_attributes(self._config_dict['stoppingDecisionMaker'], self.__simulation_components.output.output_indentation)), os.linesep)
        return_string = "{0}{1}{2}".format(return_string, "{0}SERP Impression: {1}{2}{3}".format(" "*self.__simulation_components.output.output_indentation*2, self._config_dict['serpImpression']['@class'], os.linesep, self._prettify_attributes(self._config_dict['serpImpression'], self.__simulation_components.output.output_indentation)), os.linesep)
        return_string = "{0}{1}{2}".format(return_string, "{0}Logger: {1}{2}{3}".format(" "*self.__simulation_components.output.output_indentation*2, self._config_dict['logger']['@class'], os.linesep, self._prettify_attributes(self._config_dict['logger'], self.__simulation_components.output.output_indentation)), os.linesep)
        return_string = "{0}{1}{2}".format(return_string, "{0}Search Context: {1}{2}{3}".format(" "*self.__simulation_components.output.output_indentation*2, self._config_dict['searchContext']['@class'], os.linesep, self._prettify_attributes(self._config_dict['searchContext'], self.__simulation_components.output.output_indentation)), os.linesep)
        
        return return_string

    # def __generate_search_context(self):
    #     """
    #     Generate a search context object given the settings in the configuration dictionary.
    #     """
    #     topic = self.__simulation_components.topic
    #     search_interface = self.__simulation_components.search_interface
    #     
    #     return SearchContext(search_interface=search_interface,
    #                          output_controller=self.__simulation_components.output,
    #                          topic=topic,
    #                          query_list=self.query_generator.generate_query_list(topic))
