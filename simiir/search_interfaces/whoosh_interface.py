import os
from whoosh.index import open_dir
from simiir.search_interfaces import Document
from ifind.search.cache import RedisConn
from ifind.search.engines.whooshtrec import Whooshtrec
from simiir.search_interfaces.base_interface import BaseSearchInterface
import logging

log = logging.getLogger('simuser.search_interfaces.whoosh_interface')


class WhooshSearchInterface(BaseSearchInterface):
    """
    A search interface making use of the Whoosh indexing library - and the ifind search components.

    Set model = 0 for TFIDIF
    Set model = 1 for BM25 (defaults to b=0.75), set pval to change b.
    Set model = 2 for PL2 (defaults to c=10.), set pval to change c.
    """
    def __init__(self, whoosh_index_dir, model=2, implicit_or=True, pval=None, frag_type=2, frag_size=2, frag_surround=40, host=None, port=0):
        super(WhooshSearchInterface, self).__init__()
        log.debug("Whoosh Index to open: {0}".format(whoosh_index_dir))
        self.__index = open_dir(whoosh_index_dir)
        self.__reader = self.__index.reader()
        self.__redis_conn = None
        
        if host is None:
            self._engine = Whooshtrec(whoosh_index_dir=whoosh_index_dir, model=model, implicit_or=implicit_or)
        else:
            self._engine = Whooshtrec(whoosh_index_dir=whoosh_index_dir, model=model, implicit_or=implicit_or, cache='engine', host=host, port=port)
        
        # Update (2017-05-02) for snippet fragment tweaking.
        # SIGIR Study (2017) uses frag_type==1 (2 doesn't give sensible results), surround==40, snippet_sizes==2,0,1,4
        self._engine.snippet_size = frag_size
        self._engine.set_fragmenter(frag_type=frag_type, surround=frag_surround)
        
        if pval:
            self._engine.set_model(model, pval)
    
    def issue_query(self, query, top=100):
        """
        Allows one to issue a query to the underlying search engine. Takes an ifind Query object.
        """
        query.top = top
        response = self._engine.search(query)
        
        self._last_query = query
        self._last_response = response
        return response
    
    def get_document(self, document_id):
        """
        Retrieves a Document object for the given document specified by parameter document_id.
        """
        fields = self.__reader.stored_fields(int(document_id))
        
        title = fields['title']
        content = fields['content']
        document_num = fields['docid']
        document_date = fields['timedate']
        document_source = fields['source']
        
        document = Document(id=document_id, title=title, content=content)
        document.date = document_date
        document.doc_id = document_num
        document.source = document_source
        
        return document
        
