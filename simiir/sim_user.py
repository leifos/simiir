import os
from loggers import Actions

class SimulatedUser(object):
    """
    The simulated user. Stores references to all the required components, and contains the logical workflow for the simulation.
    """
    def __init__(self, configuration):
        self.__search_context = configuration.user.search_context
        self.__decision_maker = configuration.user.decision_maker
        self.__output_controller = configuration.output
        self.__logger = configuration.user.logger
        self.__document_classifier = configuration.user.document_classifier
        self.__snippet_classifier = configuration.user.snippet_classifier
        
        self.__action_value = None  # Response from the previous action method - True or False? (did the user do or not do what they thought?)
    
    def decide_action(self):
        """
        This method is central to the whole simulation - it decides which action the user should perform next.
        The workflow implemented below is as follows. Steps with asterisks are DECISION POINTS.
        
        (1)  User issues query
        (2)  User looks at the SERP
        (3*) If the SERP looks poor, goto (1) else goto (4)
        
        (4)  Examine a snippet
        (5*) If the snippet looks at least somewhat relevant, goto (6) else decide whether to goto (1) or (4)
        
        (6)  Examine document
        (7*) If the document looks to be relevant to the provided topic, goto (8), else decide whether to goto (1) or (4)
        
        (8)  Mark the document
        (9*) Decide whether to goto (1) or (4)
        
        This method returns None.
        """
        def after_query():
            self.__do_action(Actions.SERP)
        
        def after_serp():
            if self.__action_value:
                self.__do_action(Actions.SNIPPET)
            else:
                self.__do_action(Actions.QUERY)
        
        def after_snippet():
            if self.__action_value:
                self.__do_action(Actions.DOC)
            else:
                self.__do_action(self.__do_decide())
        
        def after_assess_document():
            if self.__action_value:
                self.__do_action(Actions.MARK)
            else:
                self.__do_action(self.__do_decide())
        
        def after_mark():
            """
            This condition will always be True; we won't get here unless the document has been successfully marked!
            After the document has been marked, the user must decide whether (s)he wants to look at the subsequent snippet, or issue another query.
            """
            self.__do_action(self.__do_decide())
        
        def after_none():
            """
            If no action has been supplied from before, then we must be at the start of the search session.
            Therefore, we begin by querying.
            """
            self.__do_action(Actions.QUERY)
        
        last_to_next_action_mapping = {
            Actions.QUERY  : after_query,
            Actions.SERP   : after_serp,
            Actions.SNIPPET: after_snippet,
            Actions.DOC    : after_assess_document,
            Actions.MARK   : after_mark,
            None           : after_none
        }
        
        last_action = self.__search_context.get_last_action()
        last_to_next_action_mapping[last_action]()
    
    def __do_action(self, action):
        """
        Selects the appropriate method to call to execute the requested action, then logs the interaction in the log and search context.
        This method returns None.
        """
        action_mapping = {
            Actions.QUERY  : self.__do_query,
            Actions.SERP   : self.__do_serp,
            Actions.SNIPPET: self.__do_snippet,
            Actions.DOC    : self.__do_assess_document,
            Actions.MARK   : self.__do_mark_document
        }
        
        # Update the search context to reflect the most recent action.
        # Logging takes place within each method called (e.g. __do_query()) to reflect different values being passed.
        self.__search_context.set_action(action)
        
        # Now call the appropriate method to perform the action.
        self.__action_value = action_mapping[action]()
    
    def __do_query(self):
        """
        Called when the simulated user wishes to issue another query.
        This works by calling the search context for the subsequent query text, and is then issued to the search interface by the search context on behalf of the user.
        If no further queries are available, the logger is told of this - and the simulation will then stop at the next iteration.
        """
        query_text = self.__search_context.get_next_query()
        
        if query_text:
            self.__search_context.add_issued_query(query_text)  # Can also supply page number and page lengths here.
            self.__logger.log_action(Actions.QUERY, query=query_text)
            #self.__output_controller.log_info(info_type=None, text="Query issued: {0}".format(query_text))
            return True
        
        self.__output_controller.log_info(info_type="OUT_OF_QUERIES")
        # Tells the logger that there are no remaining queries; the logger will then stop the simulation.
        self.__logger.queries_exhausted()
        return False
    
    def __do_serp(self):
        """
        Called when the simulated user wishes to examine a SERP - the "initial glance" - after issuing a query.
        If the SERP has no results, we continue with the next action - otherwise we will always go and look at said SERP.
        """
        if self.__search_context.get_current_results_length() == 0:
            self.__logger.log_action(Actions.SERP, status="EMPTY_SERP")
            return False  # No results present; return False (we don't continue with this SERP)
        
        self.__logger.log_action(Actions.SERP, status="EXAMINE_SERP")
        return True
    
    def __do_snippet(self):
        """
        Called when the user needs to make the decision whether to examine a snippet or not.
        The logic within this method supports previous observations of the same document, and whether the text within the snippet appears to be relevant.
        """
        snippet = self.__search_context.get_current_snippet()
        self.__search_context.increment_serp_position()
        
        if self.__search_context.get_document_observation_count(snippet) > 0:
            # This document has been previously seen; so we ignore it. But the higher the count, cumulated credibility could force us to examine it?
            self.__logger.log_action(Actions.SNIPPET, status="SEEN_PREVIOUSLY", doc_id=snippet.doc_id)
            return False
        else:
            # This snippet has not been previously seen; check quality of snippet. Does it show some form of relevance?
            # If so, we return True - and if not, we return False, which moves the simulator to the next step.
            
            #print 'snippet', snippet.doc_id, self.__snippet_classifier.is_relevant(snippet)
            
            if self.__snippet_classifier.is_relevant(snippet):
                snippet.judgment = 1
                self.__logger.log_action(Actions.SNIPPET, status="SNIPPET_RELEVANT", doc_id=snippet.doc_id)
                return True
            else:
                snippet.judgment = 0
                self.__logger.log_action(Actions.SNIPPET, status="SNIPPET_NOT_RELEVANT", doc_id=snippet.doc_id)
                return False
    
    def __do_assess_document(self):
        """
        Called when a document is to be assessed.
        """
        if self.__search_context.get_last_query():
            document = self.__search_context.get_current_document()
            self.__logger.log_action(Actions.DOC, status="EXAMINING_DOCUMENT", doc_id=document.doc_id)
            
            #print 'document', document.doc_id, self.__document_classifier.is_relevant(document)
            
            if self.__document_classifier.is_relevant(document):
                document.judgment = 1
                self.__logger.log_action(Actions.DOC, status="CONSIDERED_RELEVANT", doc_id=document.doc_id)
                self.__search_context.add_relevant_document(document)
                return True
            else:
                document.judgment = 0
                self.__search_context.add_irrelevant_document(document)
                self.__logger.log_action(Actions.DOC, status="CONSIDERED_NOT_RELEVANT", doc_id=document.doc_id)
                return False
        
        return False
    
    def __do_mark_document(self):
        """
        The outcome of marking a document as relevant. At this stage, the user has decided that the document is relevant; hence True can be the only result.
        """
        document = self.__search_context.get_current_document()
        self.__logger.log_action(Actions.MARK, doc_id=document.doc_id)
        return True
    
    def __do_decide(self):
        """
        Method which returns whether a further snippet should be examined, the next query should be issued, or some other action.
        This is the "decision making" logic - and is abstracted to the instantiated DecisionMaker instance to work this out.
        """
        current_serp_length = self.__search_context.get_current_results_length()
        current_serp_position = self.__search_context.get_current_serp_position() + 1
        
        if current_serp_position > current_serp_length:
            # If this condition arises, we have reached the end of the SERP!
            # When SERP pagination is implemented, this condition will either result in moving to the next SERP page or query.
            self.__output_controller.log_info(info_type="SERP_END_REACHED")
            return Actions.QUERY
        
        return self.__decision_maker.decide()
        
    def log_query_list(self):
        self.__search_context.log_query_list()