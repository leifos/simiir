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
        return "<Topic ID: '{0}' Title: '{1}' Content: '{2}'".format(self.id, self.title, self.content)

class Topic(Document):
    """
    Extending from Document, provides the ability to read a topic title and description from a given input file.
    """
    def __init__(self, id, title=None, content=None, doc_id=None, qrels_filename=None):
        super(Topic, self).__init__(id=id, title=title, content=content, doc_id=doc_id)
        self.qrels_filename = qrels_filename
        
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