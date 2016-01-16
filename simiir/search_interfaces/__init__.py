import string

class Document(object):
    """
    Basic representation of a document - including a unique identifier (index ID), a title, document content (body), and an additional identifier (e.g. collection ID).
    Parameters title, content and the additional identifier are optional.
    """
    def __init__(self, id, title=None, content=None, doc_id=None):
        """
        Instantiates an instance of the Document.
        """
        self.id = id
        self.title = title
        self.content = content
        self.doc_id = id
        self.judgment = -1
        
        if self.doc_id:
            self.doc_id = doc_id
    
    def __str__(self):
        """
        Returns a string representation of a given instance of Document.
        """
        return "<Document ID: '{0}' Title: '{1}' Content: '{2}'".format(self.id, self.title, self.content)

class Topic(Document):
    """
    Extending from Document, provides the ability to read a topic title and description from a given input file.
    """
    def __init__(self, id, title=None, content=None, doc_id=None, qrels_filename=None, background_filename=None):
        super(Topic, self).__init__(id=id, title=title, content=content, doc_id=doc_id)
        self.qrels_filename = qrels_filename
        self.background_terms = ''
        
        if background_filename is not None:
            self._read_background(background_filename)
    
    def _read_background(self, background_filename):
        """
        Populates the background_terms attribute.
        Reads in from a file to produce a string of background terms. This is the searcher's background knowledge for a given topic.
        The background is simply stored here; you can specify in classifiers of query generators whether to consider the background.
        The input file should be a term on each line. On each line, you should have <term>,<score>.
        """
        f = open(background_filename, 'r')
        
        for line in f:
            line = line.strip().split(',')
            self.background_terms = '{prev} {new}'.format(prev=self.background_terms, new=line[0])  # Builds the string...
        
        f.close()
        
    
    def read_topic_from_file(self, topic_filename):
        """
        Attempts to open the given filename for reading and stores the contents within the given topic object.
        Assumes that the first line of the input file is the topic title, and remaining lines make up the topic description.
        """
        first_line = None
        topic_text = ''
        
        if topic_filename:
            f = open(topic_filename, 'r')
            
            for line in f:
                if not first_line:
                    first_line = line.strip()
                topic_text = topic_text + ' ' + line
        
        self.title = first_line
        self.content = topic_text

    def get_topic_text(self):
        """
        Returns a string representing the topic's title and content (description).
        """
        return '{title} {content}'.format(**self.__dict__)
    
    def get_topic_text_nopunctuation(self):
        """
        Returns a string representing the topic's title and content, with each term separated by a space.
        No punctuation is included, and all terms are lowercase.
        """
        topic_text = self.get_topic_text()
        
        topic_text = topic_text.translate(string.maketrans('', ''), string.punctuation)  # Remove punctuation from the string.
        topic_text = topic_text.replace('\n', ' ').replace('\r', '')  # Remove any newline characters.
        topic_text = topic_text.lower()  # Take everything to lowercase.
        
        return topic_text
        
    def __str__(self):
        """
        Returns a string representation of a given instance of Topic.
        """
        return "<Topic ID: '{0}' Title: '{1}' Content: '{2}'".format(self.id, self.title, self.content)
