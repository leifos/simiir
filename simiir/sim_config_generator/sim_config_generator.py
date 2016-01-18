import os
import re
import sys
import itertools
from lxml import etree
from xml.etree import cElementTree
from collections import defaultdict

simulation_base_dir = ""

def build_dictionary(input_filename):
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
    
    config_file = etree.parse(input_filename)
    string_repr = etree.tostring(config_file, pretty_print=True)
    element_tree = cElementTree.XML(string_repr)
    
    return recursive_generation(element_tree)

def tidy_dictionary(dict_repr):
    def to_list(ref, specified_type):
        if type(ref.keys()[0]) == dict:
            ref = [ref[ref.keys()[0]]]
        
        ref = ref[ref.keys()[0]]
        
        if type(ref) == dict:
            ref = [ref]
        
        for entry in ref:
            entry['type'] = specified_type
        
        return ref
    dict_repr['simulation']['topics'] = to_list(dict_repr['simulation']['topics'], 'topic')
    
    print dict_repr['simulation']['searchInterface']['@class']
    
    dict_repr['simulation']['searchInterface'] = {'class': dict_repr['simulation']['searchInterface']['@class'],
                                                  'attributes': to_list(dict_repr['simulation']['searchInterface'], 'searchInterface')}
    
    dict_repr['simulation']['user']['queryGenerator'] = to_list(dict_repr['simulation']['user']['queryGenerator'], 'queryGenerator')
    dict_repr['simulation']['user']['textClassifiers']['snippetClassifier'] = to_list(dict_repr['simulation']['user']['textClassifiers']['snippetClassifier'], 'snippetClassifier')
    dict_repr['simulation']['user']['textClassifiers']['documentClassifier'] = to_list(dict_repr['simulation']['user']['textClassifiers']['documentClassifier'], 'documentClassifier')
    dict_repr['simulation']['user']['stoppingDecisionMaker'] = to_list(dict_repr['simulation']['user']['stoppingDecisionMaker'], 'stoppingDecisionMaker')
    dict_repr['simulation']['user']['logger'] = to_list(dict_repr['simulation']['user']['logger'], 'logger')
    dict_repr['simulation']['user']['searchContext'] = to_list(dict_repr['simulation']['user']['searchContext'], 'searchContext')

def read_file_to_string(filename):
    """
    Given a filename, opens the file and returns the contents as a string.
    """
    f = open(filename, 'r')
    file_str = ""
    
    for line in f:
        file_str = "{0}{1}".format(file_str, line)
    
    f.close()
    return file_str

def get_permutations(dict_repr):
    '''
    Contains a list of tuples, with each tuple containing dictionaries representing a particular combination.
    Note that topics are ignored; these are stored within the simulation configuration file.
    '''
    query_generators = dict_repr['simulation']['user']['queryGenerator']
    snippet_classifiers = dict_repr['simulation']['user']['textClassifiers']['snippetClassifier']
    document_classifiers = dict_repr['simulation']['user']['textClassifiers']['documentClassifier']
    decision_makers = dict_repr['simulation']['user']['stoppingDecisionMaker']
    loggers =  dict_repr['simulation']['user']['logger']
    search_contexts = dict_repr['simulation']['user']['searchContext']
    
    return list(itertools.product(query_generators,
                                  snippet_classifiers,
                                  document_classifiers,
                                  decision_makers,
                                  loggers,
                                  search_contexts))

def create_attribute_markup(attribute_dict):
    """
    Given a dictionary representing an attribute, returns the associated XML markup for that attribute component.
    """
    attribute_markup = read_file_to_string('base_files/attribute.xml')
    value = attribute_dict['@value'].replace('[[ base_dir ]]', simulation_base_dir)
    
    attribute_markup = attribute_markup.format(attribute_dict['@name'],
                                               attribute_dict['@type'],
                                               value,
                                               attribute_dict['@is_argument'])
    
    return attribute_markup

def generate_topics(dict_repr):
    """
    Generates a list of XML elements representing the topic(s) to be used in the simulation.
    """
    def generate_topic_markup(entry):
        topic_markup = read_file_to_string('base_files/topic.xml')
        
        if '@backgroundFilename' in entry:
            topic_markup = read_file_to_string('base_files/topic_withbackground.xml')
            
            topic_markup = topic_markup.format(entry['@id'],
                                               entry['@filename'],
                                               entry['@qrelsFilename'],
                                               entry['@backgroundFilename'])
        else:
            topic_markup = read_file_to_string('base_files/topic.xml')
            
            topic_markup = topic_markup.format(entry['@id'],
                                               entry['@filename'],
                                               entry['@qrelsFilename'])
        
        return topic_markup
        
    topics_list = dict_repr['simulation']['topics']
    topics_str = ""
    
    for entry in topics_list:
        topics_str = "{0}{1}".format(topics_str, generate_topic_markup(entry))
    
    return topics_str

def generate_user_entries(user_permuatation_list):
    """
    Returns a series of XML components for user objects in the simulation file.
    """
    entry_list = ""
    
    for entry in user_permuatation_list:
        user_markup = read_file_to_string('base_files/user_entry.xml')
        entry_list = "{0}{1}".format(entry_list, user_markup.format(entry))
    
    return entry_list

def generate_search_interface_markup(dict_repr):
    """
    Returns markup for the search interface component.
    """
    interface_markup = read_file_to_string('base_files/interface.xml')
    interface_entry = dict_repr['simulation']['searchInterface']
    attribute_markup_concat = ''
    
    for attribute in interface_entry['attributes']:
        attribute_markup = read_file_to_string('base_files/attribute.xml')
        attribute_markup = attribute_markup.format(attribute['@name'], attribute['@type'], attribute['@value'], attribute['@is_argument'])
        attribute_markup_concat = '{0}{1}'.format(attribute_markup_concat, attribute_markup)
    
    return interface_markup.format(dict_repr['simulation']['searchInterface']['class'], attribute_markup_concat)
    
def generate_markup(dict_repr, permutations, gen_filename):
    """
    Given a tuple of dictionary objects, generates the markup for the associated simulation and its users.
    """
    user_files = []
    
    global simulation_base_dir
    simulation_base_dir = dict_repr['simulation']['@baseDir']
    
    for iteration in permutations:
        user_markup = read_file_to_string('base_files/user.xml')
        user_markup_components = {
            'id': None,
            'queryGenerator': {'class': None, 'attributes': None, 'attributes_py': None},
            'snippetClassifier': {'class': None, 'attributes': None, 'attributes_py': None},
            'documentClassifier': {'class': None, 'attributes': None, 'attributes_py': None},
            'stoppingDecisionMaker': {'class': None, 'attributes': None, 'attributes_py': None},
            'logger': {'class': None, 'attributes': None, 'attributes_py': None},
            'searchContext': {'class': None, 'attributes': None, 'attributes_py': None},
        }
        
        # Sort out the components for this iteration.
        for component in iteration:
            component_type = component['type']
            user_markup_components[component_type]['class'] = component['@name']
            
            if 'attribute' in component:
                component_attributes = component['attribute']
                user_markup_components[component_type]['attributes_py'] = component_attributes
                
                if type(component_attributes) == dict:
                    user_markup_components[component_type]['attributes'] = create_attribute_markup(component_attributes)
                else:
                    for attribute in component_attributes:
                        if user_markup_components[component_type]['attributes'] is None:
                            user_markup_components[component_type]['attributes'] = ""
                        user_markup_components[component_type]['attributes'] = "{0}{1}".format(user_markup_components[component_type]['attributes'], create_attribute_markup(attribute))
        
        # Now work out the ID.
        user_base_id = dict_repr['simulation']['user']['@baseID']
        tags = re.findall('\[\[(.*?)\]\]', user_base_id, re.DOTALL)
        tags = map(lambda x: [x,None], tags)  # Convert [x,y,z] to [[x,None], [y,None], [z,None]]
        
        for tag in tags:
            tag_name = tag[0]
            
            if tag_name.startswith('textClassifiers.'):
                tag_name = tag_name[16:]
            
            tag_split = tag_name.split('.')
            component = tag_split[0]
            
            if len(tag_split) == 2:
                attribute = tag_split[1]
            else:
                attribute = None
            
            if attribute is not None:
                for comp in iteration:
                    if comp['type'] == component and 'attribute' in comp:
                        if type(comp['attribute']) == dict:
                            if comp['attribute']['@name'] == attribute:
                                tag[1] = comp['attribute']['@value']
                        else:
                            for entry in comp['attribute']:
                                if entry['@name'] == attribute:
                                    tag[1] = entry['@value']
            
            if attribute is None or tag[1] is None:
                for comp in iteration:
                    if comp['type'] == component:
                        tag[1] = comp['@name']
            
            # Replace the string instance with the tag!
            user_base_id = user_base_id.replace("[[" + tag[0] + "]]", tag[1])
        
        user_files.append(os.path.join(dict_repr['simulation']['@baseDir'], "user-{0}.xml").format(user_base_id))
        
        user_markup = read_file_to_string('base_files/user.xml')
        user_markup = user_markup.format(
            user_base_id,
            user_markup_components['queryGenerator']['class'],
            user_markup_components['queryGenerator']['attributes'] if user_markup_components['queryGenerator']['attributes'] is not None else "",
            user_markup_components['snippetClassifier']['class'],
            user_markup_components['snippetClassifier']['attributes'] if user_markup_components['snippetClassifier']['attributes'] is not None else "",
            user_markup_components['documentClassifier']['class'],
            user_markup_components['documentClassifier']['attributes'] if user_markup_components['documentClassifier']['attributes'] is not None else "",
            user_markup_components['stoppingDecisionMaker']['class'],
            user_markup_components['stoppingDecisionMaker']['attributes'] if user_markup_components['stoppingDecisionMaker']['attributes'] is not None else "",
            user_markup_components['logger']['class'],
            user_markup_components['logger']['attributes'] if user_markup_components['logger']['attributes'] is not None else "",
            user_markup_components['searchContext']['class'],
            user_markup_components['searchContext']['attributes'] if user_markup_components['searchContext']['attributes'] is not None else "")
        
        user_file = open('output/user-{0}.xml'.format(user_base_id), 'w')
        user_file.write(user_markup)
        user_file.close()
        
    # Generate the markup!
    
    users = generate_user_entries(user_files)
    topics = generate_topics(dict_repr)
    search_interface = generate_search_interface_markup(dict_repr)
    
    simulation_markup = read_file_to_string('base_files/simulation.xml')
    simulation_markup = simulation_markup.format(dict_repr['simulation']['@baseID'],
                                                 os.path.join(dict_repr['simulation']['@baseDir'], 'out'),
                                                 topics,
                                                 users,
                                                 search_interface)
    
    # New - handle generators with different bits at the end
    gen_filenamesplit = gen_filename.split('-')
    
    if len(gen_filenamesplit) > 1:
        end_filename = '-'.join(gen_filenamesplit[1:])
        end_filename = end_filename[:-4]
    else:
        end_filename = dict_repr['simulation']['@baseID']
    # End new
    
    simulation_file = open('output/simulation-{0}.xml'.format(end_filename), 'w')
    simulation_file.write(simulation_markup)
    simulation_file.close()

def clear_output_dir():
    """
    Clears the output directory.
    """
    folder = 'output/'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            print e
    
    if not os.path.exists('output/out'):
        os.makedirs('output/out/')
    f = open('output/out/CREATED', 'w')
    f.close()

def usage(filename):
    """
    Prints the usage to stdout.
    """
    print "Usage: python {0} <xml_source>".format(filename)
    print "Where:"
    print "  <xml_source>: the source XML file from which to generate simulation configuration files. See example.xml."

if __name__ == '__main__':
    if len(sys.argv) > 1 and len(sys.argv) < 3:
        clear_output_dir()
        dict_repr = build_dictionary(sys.argv[1])
        tidy_dictionary(dict_repr)
        
        permutations = get_permutations(dict_repr)
        generate_markup(dict_repr, permutations, sys.argv[1])
        
        sys.exit(0)
    
    # Invalid number of command-line parameters, print usage.
    usage(sys.argv[0])
    sys.exit(1)