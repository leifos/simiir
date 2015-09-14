import os
from loggers import Actions
from ifind.search.query import Query
from search_interfaces import Document
import logging

log = logging.getLogger('search_context.search_context')

class SearchContext(object):
    """
    The "memory" of the simulated user. Contains details such as the documents that have been examined by the user.
    This class also provides a link between the simulated user and the search engine interface - allowing one to retrieve the next document, snippet, etc.
    """
    def __init__(self, search_interface, output_controller, topic, query_list=[], query_limit=None):
        """
        Several instance variables here to track the different aspects of the search process.
        """
        self._search_interface = search_interface
        self._output_controller = output_controller
        self._topic = topic
        
        self._actions = []                       # A list of all of the actions undertaken by the simulated user in chronological order.
        self._depths = []                        # Documents and snippets examined for previous queries.
        
        self._query_list = query_list            # The list of queries to issue.
        self._query_count = 0                    # The total number of queries issued.
        self._last_query = None                  # The Query object that was issued.
        self._last_results = None                # Results for the query.
        self._issued_queries = []                # A list of queries issued in chronological order.
        
        self._current_serp_position = 0          # The position in the current SERP we are currently looking at (zero-based!)
                                                  # This counter is used for the current snippet and document.
        
        self._snippets_examined = []             # Snippets that have been previously examined.
        self._documents_examined = []            # Documents that have been previously examined.
        
        self._previously_examined_snippets = []  # A list of all snippets that have been seen more than once across the search session.
        self._all_snippets_examined = []         # A list of all snippets examined throughout the search session.
        self._all_documents_examined = []        # A list of all documents examined throughout the search session.
        
        self._relevant_documents = []            # All documents marked relevant throughout the search session.
        self._irrelevant_documents = []          # All documents marked irrelevant throughout the search session.
        
        if type(query_limit) == int and query_limit > 0:
            self._query_list = self._query_list[0:query_limit]
    
    def report(self):
        """
        Returns basic statistics held within the search context at the time of calling.
        Ideally, call at the end of the simulation for a complete set of stats.
        """
        return_string = "    Number of Queries Issued: {0}{1}".format(self._query_count, os.linesep)
        return_string = return_string + "    Number of Snippets Examined: {0}{1}".format(len(self._all_snippets_examined), os.linesep)
        return_string = return_string + "    Number of Documents Examined: {0}{1}".format(len(self._all_documents_examined), os.linesep)
        return_string = return_string + "    Number of Documents Marked Relevant: {0}".format(len(self._relevant_documents))
        
        self._output_controller.log_info(info_type="SUMMARY")
        self._output_controller.log_info(info_type="TOTAL_QUERIES_ISSUED", text=self._query_count)
        self._output_controller.log_info(info_type="TOTAL_SNIPPETS_EXAMINED", text=len(self._all_snippets_examined))
        self._output_controller.log_info(info_type="TOTAL_DOCUMENTS_EXAMINED", text=len(self._all_documents_examined))
        self._output_controller.log_info(info_type="TOTAL_DOCUMENTS_MARKED_RELEVANT", text=len(self._relevant_documents))
        
        return return_string
        
    def show_query_list(self):
        for q in self._query_list:
            print q

    def log_query_list(self):
        for q in self._query_list:
            log.debug(q)


    def get_last_action(self):
        """
        Returns the last action performed by the simulated user.
        If no previous action is present, None is returned - this is only true at the start of a simulated search session.
        """
        if self._actions:
            last_action = self._actions[-1]
        else:
            last_action = None
        
        return last_action
    
    def set_action(self, action):
        """
        This method is key - depending on the action that is passed to it, the relevant method handling the tidying up for that action is called.
        This is the publicly exposed method for doing some action.
        """
        action_mappings = {
            Actions.QUERY:   self._set_query_action,
            Actions.SERP:    self._set_serp_action,
            Actions.SNIPPET: self._set_snippet_action,
            Actions.DOC:     self._set_assess_document_action,
            Actions.MARK:    self._set_mark_action
        }
        
        if action_mappings[action]:
            self._actions.append(action)
            action_mappings[action]()
    
    def _set_query_action(self):
        """
        Called when a new query is issued by the simulated user.
        Resets the appropriate counters for the next iteration; stores the previously examined snippets and documents for reference.
        """
        if self._query_count > 0:
            #  If a query has been issued previously, store the snippets and documents examined for reference later on.
            self._depths.append((self._snippets_examined, self._documents_examined))

        # Reset our counters for the next query.
        self._snippets_examined = []
        self._documents_examined = []
        
        self._current_document = None
        self._current_snippet = None
        
        self._current_serp_position = 0
    
    def _set_serp_action(self):
        """
        Method called when a SERP is initially examined.
        Any modifications to the search context can be undertaken here.
        """
        pass
    
    def _set_snippet_action(self):
        """
        Called when a snippet is to be examined for relevance.
        Updates the corresponding instance variables inside the search context to reflect a new snippet.
        """
        # Pull out the next result, and construct a Document object representing the snippet. Set the current snippet to that Document.
        result = self._last_results[self._current_serp_position]
        snippet = Document(result.whooshid, result.title, result.summary, result.docid)

        self._snippets_examined.append(snippet)
        self._all_snippets_examined.append(snippet)
        self._current_snippet = snippet
        
        # Sets the current document
        self._current_document = self._search_interface.get_document(snippet.id)
        
    def get_current_snippet(self):
        """
        Returns the current snippet object. Returns None if no query has been issued.
        """
        return self._current_snippet
        
    def _set_assess_document_action(self):
        """
        Called when a document is to be assessed for relevance.
        """
        self._documents_examined.append(self._current_document)
        self._all_documents_examined.append(self._current_document)
    
    def _set_mark_action(self):
        """
        Called when the currently examined document is to be marked as relevant.
        """
        pass
    
    def get_next_query(self):
        """
        Returns the string representation of the next query.
        If no further queries are available, None is returned.
        """
        query_text = None
        
        if len(self._query_list) > self._query_count:
            query_text = self._query_list[self._query_count][0]  # We only want the query terms, not the scores - hence [0]
            self._query_count = self._query_count + 1
        
        return query_text
    
    def add_issued_query(self, query_text, page=1, page_len=1000):
        """
        Adds a query to the stack of previously issued queries.
        """
        def create_query_object():
            """
            Nested method which returns a Query object for the given query string, page number and page length attributes from the parent method.
            """
            query_object = Query(query_text)
            query_object.skip = page
            query_object.top = page_len
            
            response = self._search_interface.issue_query(query_object)
            query_object.response = response
            
            return query_object
        
        # Obtain the Query object and append it to the issued queries list.
        query_object = create_query_object()
        
        self._issued_queries.append(query_object)
        self._last_query = query_object
        self._last_results = self._last_query.response.results
    
    def get_last_query(self):
        """
        Returns the previous query issued. If no previous query has been issued, None is returned.
        """
        return self._last_query
    
    def get_document_observation_count(self, selected_document):
        """
        Returns a zero or positive integer representing the number of times the simulated user has seen the given document in previous SERPs.
        If the returned value is 0, the document is new to the user, otherwise the document has been seen as many times as the returned value.
        """
        occurrences = 0
        
        for document in self._all_documents_examined:
            if document.doc_id == selected_document.doc_id:
                occurrences = occurrences + 1
        
        return occurrences
    
    def get_snippet_observation_count(self, selected_snippet):
        """
        Returns a zero or positive integer representing the number of times the simulated user has seen the given snippet in previous SERPs.
        If the returned value is 0, the document is new to the user, otherwise the snippet has been seen as many times as the returned value.
        """
        occurrences = 0
        
        for snippet in self._all_snippets_examined:
            if snippet.doc_id == selected_snippet.doc_id:
                occurrences = occurrences + 1
        
        return occurrences
    
    def get_snippet_observation_judgment(self, selected_snippet):
        """
        Returns the historic judgment for a snippet.
        If the snippet passed has not been seen previously, -1 will be returned.
        """
        if self.get_snippet_observation_count(selected_snippet) > 0:
            for snippet in self._all_snippets_examined:
                if snippet.doc_id == selected_snippet.doc_id:
                    if snippet.judgment > -1:
                        return snippet.judgment
        
        return -1
    
    def get_current_document(self):
        """
        Returns the current document. If no query has been issued, None is returned.
        """
        return self._current_document
    
    def add_relevant_document(self, document):
        """
        Adds the given document to the relevant document list.
        """
        self._relevant_documents.append(document)
    
    def get_relevant_documents(self):
        """
        Returns the list of documents marked relevant throughout the simulation.
        """
        return self._relevant_documents
    
    def add_irrelevant_document(self, document):
        """
        Adds the given document to the irrelevant document list.
        """
        self._irrelevant_documents.append(document)
    
    def get_current_serp_position(self):
        """
        Returns the current rank we are looking at within the current SERP.
        """
        return self._current_serp_position# + 1
    
    def get_current_results_length(self):
        """
        If a current set of results for a SERP is present, returns the number of results returned.
        If the previous query returns no results, 0 will always be returned.
        """
        if self._last_results:
            return len(self._last_results)
        
        return 0
    
    def get_topic(self):
        """
        Returns the topic Document object.
        """
        return self._topic
    
    def increment_serp_position(self):
        """
        Increments the counter representing the current rank on the SERP by 1.
        """
        self._current_serp_position = self._current_serp_position + 1
    
    def reached_end_of_serp(self):
        """
        Returns True iif the current position of the SERP has exceeded the number of results available on the SERP (e.g. EOF).
        This result is used when determining what to do next.
        """
        return self._current_serp_position == len(self._last_results)

    def get_examined_snippets(self):
        """
        Returns a list of Document objects representing all of the snippets examined by the simulated agent for the current query.
        The most recent snippet to be examined is the last document in the list - i.e. snippets are listed in chronological order.
        An empty list indicates that no snippets have been examined for the current query.
        """
        return self._snippets_examined
    
    def get_all_examined_snippets(self):
        """
        Returns a list of Document objects representing all of the snippets examined by the simulated agent over the given search session.
        The most recent snippet to be examined is the last document in the list - i.e. snippets are listed in chronological order.
        An empty list indicates that no snippets have been examined in the entire search session.
        """
        return self._all_snippets_examined
    
    def get_examined_documents(self):
        """
        Returns a list of Document objects representing all of the documents examined by the simulated agent for the current query.
        The most recent document examined is the last document in the list - i.e. examined documents are listed in chronological order.
        An empty list indicates that no documents have been examined for the current query.
        """
        return self._documents_examined
    
    def get_all_queries(self):
        """
        Returns a list of all queries generated.
        """
        return self._query_list
    
    def get_issued_queries(self):
        """
        Returns a list of all queries that have been issued for the given search session.
        """
        return self._issued_queries