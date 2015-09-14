from search_contexts.search_context import SearchContext

class SearchContextRevisedRelevance(SearchContext):
    """
    The memory of the simulated user - who decides that documents are not relevant have their snippets not relevant to.
    """
    def __init__(self, search_interface, output_controller, topic, query_list=[], query_limit=None):
        super(SearchContextRevisedRelevance, self).__init__(search_interface,
                                                            output_controller,
                                                            topic,
                                                            query_list,
                                                            query_limit)
        
    def add_irrelevant_document(self, document):
        """
        Overrides the base search context's add_irrelevant_document() method.
        In the case of a document being considered non relevant, we change the snippet jugdement for said document to non-relevant, too.
        """
        
        snippets = self.get_examined_snippets()
        
        for snippet in snippets:
            if document.doc_id == snippet.doc_id:
                snippet.judgment = 0
        
        super(SearchContextRevisedRelevance, self).add_irrelevant_document(document)