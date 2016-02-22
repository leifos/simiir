import os
import abc
from lxml import etree
from xml.etree import cElementTree
from collections import defaultdict
from simiir.config_readers import ConfigReaderError

class BaseConfigReader(object):
    """
    The base Configuration Reader class. Extend this class to implement additional configuration file types.
    This base includes by default the ability to validate a supplied configuration file with a supplied DTD schema.
    If no DTD schema is supplied (dtd_filename==None), then no DTD validation takes place.
    """
    def __init__(self, config_filename=None, dtd_filename=None):
        self._config_filename = config_filename

        dtd_path = os.path.join( os.path.dirname(__file__),'dtds')

        self._dtd_filename = os.path.join(dtd_path, dtd_filename)

        if self._config_filename is None:
            raise ConfigReaderError("No configuration file has been specified.")
        else:
            self._config_file = etree.parse(self._config_filename)
        
        self.__validate_against_dtd()
        self.__build_dictionary()
        self._validate_config()
    
    def __validate_against_dtd(self):
        """
        Parses the configuration file and checks its validity compared to the DTD specification.
        """
        # Opens the DTD file and loads it into a lxml DTD object.
        dtd_file = open(self._dtd_filename, 'r')
        dtd_object = etree.DTD(dtd_file)


        # .validate() checks if the config file complies to the schema. If it doesn't, this condition is entered.
        if not dtd_object.validate(self._config_file):
            dtd_file.close()
            raise ConfigReaderError("DTD validation failed on {0}: {1}".format(self._config_filename,
                                                                               dtd_object.error_log.filter_from_errors()[0]))

        # If we get here, the validation passed, so we can close the DTD file object.
        dtd_file.close()
    
    def __build_dictionary(self):
        """
        Turns the XML configuration file into a Python dictionary object.
        The nested function recursive_generation() is unsurprisingly recursive.
        """
        def recursive_generation(t):
            """
            Nested helper function that recursively loops through an XML node to construct a dictionary.
            Solution from http://stackoverflow.com/a/10077069 (2013-01-19)
            """
            d = {t.tag: {} if t.attrib else None}
            children = list(t)

            if children:
                dd = defaultdict(list)

                for dc in map(recursive_generation, children):
                    for k, v in dc.iteritems():
                        dd[k].append(v)

                d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}

            if t.attrib:
                d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())

            if t.text:
                text = t.text.strip()

                if children or t.attrib:
                    if text:
                        d[t.tag]['#text'] = text
                else:
                    d[t.tag] = text

            return d
        
        string_repr = etree.tostring(self._config_file, pretty_print=True)
        element_tree = cElementTree.XML(string_repr)
        
        self._config_dict = recursive_generation(element_tree)
        self._config_dict = self._config_dict[self._config_dict.keys()[0]]
    
    @abc.abstractmethod
    def _validate_config(self):
        """
        An abstract method. Implement this to ensure that the settings supplied in the configuration file are correct for the given configuration schema (e.g. correct types).
        This is run under the assumption that the XML is well formed.
        """
        pass