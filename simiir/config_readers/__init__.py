import os
import string

class ConfigReaderError(Exception):
    """
    A special Exception which is raised when something is incorrect with the configuration file.
    """
    pass

def parse_boolean(boolean_value):
	"""
	Given a string (boolean_value), returns a boolean value representing the string contents.
	For example, a string with 'true', 't', 'y' or 'yes' will yield True.
	"""
	boolean_value = string.lower(boolean_value) in ('yes', 'y', 'true', 't', '1')
	return boolean_value

def empty_string_check(string, raise_exception = True):
	"""
	Simple check to see if the string provided by parameter string is empty. False indicates that the string is NOT empty.
	Parameter raise_exception determines if a ValueError exception should be raised if the string is empty. If raise_exception is False and the string is empty, True is returned.
	"""
	if string != '':
		return False

	if raise_exception:
		raise ValueError("Empty string detected!")

	return True

def check_attributes(config_entry):
    """
    Checks a series of attribute nodes, or a single attribute node.
    The name, type and is_argument parameters should be specified - only value can be a blank value.
    """
    def do_check(single):
        """
        Nested helper function - checks a single attribute node.
        """
        empty_string_check(single['@name'])
        empty_string_check(single['@type'])
        empty_string_check(single['@is_argument'])
        
        single['@is_argument'] = parse_boolean(single['@is_argument'])
        
        if single['@type'] not in ['string', 'integer', 'float', 'boolean']:
            raise ConfigReaderError("Invalid attribute type: '{0}'".format(single['@type']))
        else:
            if single['@type'] == 'integer':
                single['@value'] = int(single['@value'])
            elif single['@type'] == 'float':
                single['@value'] = float(single['@value'])
            elif single['@type'] == 'boolean':
                single['@value'] = parse_boolean(single['@value'])
    
    if 'attribute' in config_entry:
        if type(config_entry['attribute']) == list:
            for entry in config_entry['attribute']:
                do_check(entry)
        else:
            do_check(config_entry['attribute'])

def filesystem_exists_check(path, raise_exception = True):
	"""
	Checks to see if the path, specified by parameter path, exists. Can be either a directory or file. If the path exists, True is returned. If the path does not exist, and raise_exception is set to True, an IOError is raised - else False is returned.
	"""
	if os.path.lexists(path):
		return True

	if raise_exception:
		raise IOError("Could not find the specified path, %s." % (path))

	return False