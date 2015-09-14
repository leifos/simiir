import os
import abc
import inspect
import importlib

class BaseComponentGenerator(object):
    """
    The base Component Generator. Given a configuration dictionary, contains functionality to generate Python objects to be used for a simulation.
    Extend this class to include additional functionality for other components. Any extended classes should instantiate objects as attriutes in the constructor.
    """
    def __init__(self, config_dict):
        self._config_dict = config_dict
    
    @abc.abstractmethod
    def prettify(self):
        """
        Abstract method.
        Returns a prettified string representation of the configuration dictionary.
        """
        return self._config_dict
    
    def _prettify_attributes(self, config_entry, indentation_level):
        """
        Given a configuration entry, returns any attributes for said configuration entry in a readable string representation, with one attribute per line.
        """
        def get_string_representation(singular):
            return "{0}: {1}{2}".format(singular['@name'], str(singular['@value']), os.linesep)
        
        indent_level = indentation_level * 2
        string_representation = ""
        
        if 'attribute' in config_entry:
            if type(config_entry['attribute']) == list:
                for entry in config_entry['attribute']:
                    string_representation = "{0}{1}{2}".format(string_representation, "  "*indent_level, get_string_representation(entry))
            else:
                string_representation = "{0}{1}".format("  "*indent_level, get_string_representation(config_entry['attribute']))
        
        if len(string_representation) > 0 and string_representation[-1] == os.linesep:
            return string_representation[:-1]
        
        return string_representation
    
    def _get_object_reference(self, config_details, package, components=[]):
        """
        Given a configuration dictionary for a particular class, a package, and an optional list of components...
        Returns an object reference which can be used as part of the simulation.
        """
        selected_class = config_details['@class']
        available_classes = self.__get_available_classes(package)
        attributes = self.__get_attributes(config_details)
        
        for available_class in available_classes:
            if available_class[0] == selected_class:
                kwargs = {}
                
                # Add all attributes to kwargs to pass to the constructor of the object.
                for attribute in attributes:
                    if attribute['@is_argument']:
                        kwargs[attribute['@name']] = attribute['@value']
                
                # For any component attributes (e.g. Topic, SearchContext)...add to kwargs!
                for attribute_reference in components:
                    kwargs[attribute_reference[0]] = attribute_reference[1]
                
                reference = available_class[1](**kwargs)
                
                # If any attributes for the new object are required, now we pass them.
                for attribute in attributes:
                    if not attribute['@is_argument']:
                        setattr(reference, attribute['@name'], attribute['@value'])
                
                # The instance should be now instantiated!
                return reference
        
        raise ImportError("Specified class '{0}' could not be found.".format(selected_class))
    
    def __get_available_classes(self, package):
        """
        Given a Python package name within the simuser package, returns a list of available classes within said package.
        This method uses reflection to work out which classes exist.
        """
        modules = []
        classes = []
        
        # List through the modules in the specified package, ignoring __init__.py, and append them to a list.
        for f in os.listdir(package):
            if f.endswith('.py') and not f.startswith('__init__'):
                modules.append('{0}.{1}'.format(package, os.path.splitext(f)[0]))
        
        module_references = []
        
        # Attempt to import each module in turn so we can access its classes
        for module in modules:
            module_references.append(importlib.import_module(module))
        
        # Now loop through each module, looking at the classes within it - and then append each class to a list of valid classes.
        for module in module_references:
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    classes.append((obj.__name__, obj))
        
        return classes
    
    def __get_attributes(self, config_details):
        """
        Returns a consistent list of attributes from the given configuration dictionary.
        """
        attributes = []

        if 'attribute' in config_details:
            if type(config_details['attribute']) == dict:
                attributes.append(config_details['attribute'])
            else:
                attributes = config_details['attribute']

        return attributes