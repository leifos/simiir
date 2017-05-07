from simiir.utils.tidy import clean_html
from simiir.search_interfaces import Document
from simiir.serp_impressions import SERPImpression
from simiir.serp_impressions.base_serp_impression import BaseSERPImpression
from simiir.text_classifiers.lm_topic_classifier import TopicBasedLMTextClassifier

class LMSERPImpression(BaseSERPImpression):
    """
    A language modelling based approach to judging how good a SERP appears to be.
    Typically, you'll want to make this quite liberal to increase the likelihood of a searcher deciding to enter the SERP, judging snippets.
    """
    def __init__(self, search_context, topic, viewport_size, dcg_discount, patch_type_threshold):
        super(LMSERPImpression, self).__init__(search_context, topic, dcg_discount, patch_type_threshold)
        self.__classifier = None
        
        # All of the following attributes can be changed from the configuration file (defaults provided below).
        self.viewport_size = viewport_size  # How many snippets can be seen in the user's viewport?
        self.query_time = 5  # Time spent querying
        self.avg_dcg_threshold = 0.0  # Threshold for average rate of DCG
        
        # The following attributes are used to initialise the TopicBasedLMTextClassifier classifier.
        self.classifier_title_only = True  # Used to examine snippet titles only; False will examine the title and snippet text.
        self.classifier_method = 'jm'
        self.classifier_lam = 0.0
        self.classifier_thresh = 0.0
        self.classifier_title_weighting = 1
        self.classifier_topic_weighting = 1
        self.classifier_topic_background_weighting = 1
        self.classifier_document_weighting = 1
        self.classifier_stopword_file = []
        self.classifier_background_file = []
    
    def initialise(self):
        """
        Initialises the classifier (if not already instantiated); judges the given SERP.
        """
        if self.__classifier is None:
            # Instantiate the classifier using the settings provided as attributes to the SERP impression class.
            self.__classifier = TopicBasedLMTextClassifier(self._topic,
                                                           self._search_context,
                                                           self.classifier_stopword_file,
                                                           self.classifier_background_file,
                                                           self.classifier_topic_weighting,
                                                           self.classifier_topic_background_weighting,
                                                           self.classifier_document_weighting)
                                                          
            self.__classifier.method = self.classifier_method
            self.__classifier.lam = self.classifier_lam
            self.__classifier.threshold = self.classifier_thresh
            self.__classifier.title_weight = self.classifier_title_weighting
            self.__classifier.topic_weighting = self.classifier_topic_weighting
            self.__classifier.topic_background_weighting = self.classifier_topic_background_weighting
            self.__classifier.document_weighting = self.classifier_document_weighting
            self.__classifier.updating = False  # Assume that the classifier does not update.
            self.__classifier.update_method = 1
            self.__classifier.title_only = self.classifier_title_only
    
    def get_impression(self):
        """
        Determines if the SERP is attractive enough to examine in more detail.
        Uses Discounted Cumulative Gain (DCG) to ascertain if the rate of expected gain is high enough to peruse the SERP in more detail.
        Returns the judgement (True/False to continue or not) and the calculated patch type.
        """
        dis_cum_gain = 0.0
        pos = 0.0
        results_len = self._search_context.get_current_results_length()
        results_list = self._search_context.get_current_results()
        viewport_size = self.viewport_size
        
        # In the eventuality the number of results is less than the viewport size, change the target value (viewport_size).
        if results_len < self.viewport_size:
            viewport_size = results_len
        
        judgements = []
            
        # Iterate through the viewable snippets...
        for i in range(0, viewport_size):
            snippet = Document(results_list[i].whooshid, results_list[i].title, results_list[i].summary, results_list[i].docid)
            pos = pos + 1.0
            
            j = 0
            
            if self.__classifier.is_relevant(snippet):
                j = 1
                
            if j < 0:
                j = 0
            
            judgements.append(j)
            dis_cum_gain += (j)*(1.0/(pos**self._dcg_discount))
            
        total_time = float(self.query_time)
        avg_dis_cum_gain = dis_cum_gain / total_time
        
        patch_type = self._calculate_patch_type(judgements)  # Calculate the patch type.
        judgement = False  # We want to abandon the SERP and then proceed to the next action.
        
        if avg_dis_cum_gain >= self.avg_dcg_threshold:
            judgement = True  # We want to examine the SERP in more detail
        
        return SERPImpression(judgement, patch_type)