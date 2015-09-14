import os

class OutputController(object):
    """
    
    """
    def __init__(self, simulation_configuration, output_configuration):
        self.__simulation_configuration = simulation_configuration
        
        self.__base_directory = output_configuration['@baseDirectory']
        self.__save_interaction_log_flag = output_configuration['@saveInteractionLog']
        self.__save_relevance_judgments_flag = output_configuration['@saveRelevanceJudgments']
        self.__trec_eval_flag = output_configuration['@trec_eval']
        
        self.__interaction_log = []
        self.__query_log = []
        
        self.output_indentation = 2  # Controls the level of indentation when outputting results to stdout.
                                     # Publicly facing instance variable - is used by the Component Generators prettify() methods.
    
    def log(self, entry):
        """
        Adds an event to the interaction log.
        For informational log entries (not actions) call log_info().
        """
        self.__interaction_log.append(entry)
    
    def log_info(self, info_type=None, text=""):
        """
        Logs additional information to the interaction log which may be useful when supplemented with action log entries.
        For example, you could include statistics at the end of the log file with this command.
        
        Entries are logged in the format
        INFO <info_type> <text>
        If <info_type> is None, then FREETEXT will be used.
        
        Specify info_type to indicate the data being presented (e.g. NUMBER_RELEVANT_DOCUMENTS_MARKED).
        Use text to present the information.
        """
        if info_type is None:
            info_type = "CUSTOM"
        
        self.__interaction_log.append("INFO {0} {1}".format(info_type, text))
    
    def log_query(self, query):
        """
        Logs a generated query, ready to save it to the query output file.
        """
        self.__query_log.append(query)
        
    def display_config(self):
        """
        Sends a prettified version of the current simulation's configuration to stdout.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        
        simulation_base_id = self.__simulation_configuration.base_id
        print "SIMULATION '{0}'".format(simulation_base_id)
        
        print "{0}Simulation Configuration:".format(" "*self.output_indentation)
        print self.__simulation_configuration.prettify()

        print "{0}User Configuration ({1}):".format(" "*self.output_indentation, self.__simulation_configuration.user.id)
        print self.__simulation_configuration.user.prettify()
        
    def display_report(self):
        """
        Prints a summary of the results from the simulation to stdout.
        """
        search_context_summary = self.__simulation_configuration.user.search_context.report()
        
        print
        print
        print "{0}Results Summary:".format(" "*self.output_indentation)
        print "{0}{1}".format(search_context_summary, os.linesep)
    
    def save(self):
        """
        Publicly exposed function used for saving all output files to disk.
        Calls a private method for each in turn - whether or not the files are saved is dependent upon the set flags.
        """
        self.__save_interaction_log()
        self.__save_relevance_judgments()
        self.__save_query_log()
        self.__run_trec_eval()
    
    def __save_interaction_log(self):
        """
        Depending on the status of the interaction log flag, saves the interaction log to disk.
        """
        if self.__save_interaction_log_flag:
            interaction_log_filename = '{0}.log'.format(self.__simulation_configuration.base_id)
            interaction_log_filename = os.path.join(self.__base_directory, interaction_log_filename)
            
            log_file = open(interaction_log_filename, 'w')
            
            for entry in self.__interaction_log:
                log_file.write('{0}{1}'.format(entry, os.linesep))
            
            log_file.close()
    
    def __save_query_log(self):
        """
        Saves the query log to the output file.
        """
        query_log_filename = '{0}.queries'.format(self.__simulation_configuration.base_id)
        query_log_filename = os.path.join(self.__base_directory, query_log_filename)
        
        log_file = open(query_log_filename, 'w')
        
        for entry in self.__query_log:
            log_file.write('{0}{1}'.format(entry, os.linesep))
        
        log_file.close()
    
    def __save_relevance_judgments(self):
        """
        Depending on the status of the relevance judgments flag, saves relevance judgments to disk.
        """
        if self.__save_relevance_judgments_flag:
            search_context = self.__simulation_configuration.user.search_context
            topic = self.__simulation_configuration.topic
            
            relevance_judgments_filename = '{0}.rels'.format(self.__simulation_configuration.base_id)
            relevance_judgments_filename = os.path.join(self.__base_directory, relevance_judgments_filename)
            
            rank = 0
            
            with open(relevance_judgments_filename, 'w') as judgments_file:
                for document in search_context.get_relevant_documents():
                    rank = rank + 1
                    judgments_file.write("{0} Q0 {1} {2} {3} Exp{4}".format(topic.id, document.doc_id, rank, rank, os.linesep))
    
    def __run_trec_eval(self):
        """
        Runs trec_eval over the relevance judgments created by the simulator. Produces a .out file.
        This only runs if the relevance judgments and trec_eval flags are set.
        Assume trec_eval is on your path.
        """
        if self.__save_relevance_judgments_flag and self.__trec_eval_flag:
            relevance_judgments_filename = '{0}.rels'.format(self.__simulation_configuration.base_id)
            relevance_judgments_filename = os.path.join(self.__base_directory, relevance_judgments_filename)
            
            qrels_filename = os.path.abspath(self.__simulation_configuration.topic.qrels_filename)
            
            output_filename = '{0}.out'.format(self.__simulation_configuration.base_id)
            output_filename = os.path.join(self.__base_directory, output_filename)
            
            os.system('trec_eval {0} {1} > {2}'.format(qrels_filename, relevance_judgments_filename, output_filename))