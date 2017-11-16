import abc
import numpy
from simiir.search_interfaces import Document
from simiir.serp_impressions import PatchTypes
from simiir.utils.data_handlers import get_data_handler

class BaseSERPImpression(object):
    """
    A base class implementation of the SERP impression component.
    Contains the abstract signature for the is_serp_attractive() method.
    Also contains a concrete implementation to determine the patch quality, as per Stephen and Krebs (1986).
    """
    def __init__(self, search_context, qrel_file, host=None, port=None):
        self._search_context = search_context
        
        # Default values - set as attributes in the coniguration to change these values.
        self.dcg_discount = 0.5
        self.patch_type_threshold = 0.6
        self.viewport_size = 10
        self.novel_snippets_only = False
        
        self._qrel_data_handler = get_data_handler(filename=qrel_file, host=host, port=port, key_prefix='serpimpressions')
    
    
    def __get_scores(self, judgements):
        """
        Calculates the score for a given set of judgements.
        """
        cumulative_sum = numpy.cumsum(judgements)
        return sum(cumulative_sum)
    
    def _calculate_patch_type(self, snippet_judgements=None):
        """
        Given a series of snippet judgements (as an ordered list, with 1=relevant, 0=non-relevant), works out the
        patch type as per Stephen and Krebs (1986), Section 8.3. To calculate how good a SERP is judged to appear,
        we use the rate of gain per document -- up to the value of the viewport_size variable.
        
        We normalise the value between 0 and 1 by considering a set of judgements all set to 1 as the maximum, and
        working out the normalised value for the given snippet judgements. Again, viewport_size is again used to work this out.
        
        Relevant documents at higher ranks have 
        
        This method can probably be spun out into a separate component in the future; for now, a single approach is sufficient.
        """
        max_size = self.viewport_size
        
        if snippet_judgements is None or len(snippet_judgements) == 1:
            return PatchTypes.UNDEFINED
        
        if len(snippet_judgements) < max_size:
            max_size = len(snippet_judgements)
        
        perfect_judgements = [1] * max_size
        perfect_score = self.__get_scores(perfect_judgements)
        
        judgements_score = self.__get_scores(snippet_judgements)
        normalised_score = float(judgements_score) / perfect_score
        
        if normalised_score >= self.patch_type_threshold:
            return PatchTypes.EARLY_GAIN
        
        return PatchTypes.GRADUAL_INCREASE
        
        # # Old code.
        # # Used DCG and area under curves. The code above is more straightforward.
        # def calculate_maximum_area(snippet_judgements_length):
        #     """
        #     Given a length parameter, returns the maximum area under the curve if all documents up to
        #     length snippet_judgements_length are judged to be relevant.
        #     """
        #     perfect_judgements = [1] * snippet_judgements_length
        #     cumulative_perfect_judgements = numpy.cumsum(perfect_judgements)
        #     return float(numpy.trapz(cumulative_perfect_judgements, dx=snippet_judgements_length))
        #
        #
        # if snippet_judgements is None or len(snippet_judgements) == 1:
        #     return PatchTypes.UNDEFINED
        #
        # no_snippets = len(snippet_judgements)
        #
        # # Calculate the DCG at each rank, with the DCG threshold specified.
        # dcg_values = []
        #
        # for i in range(0, len(snippet_judgements)):
        #     dcg = snippet_judgements[i] * (1.0/(i+1)**self.dcg_discount)
        #     dcg_values.append(dcg)
        #
        # cumulative = numpy.cumsum(dcg_values)
        # area = numpy.trapz(cumulative, dx=no_snippets)
        #
        # # Produce a ratio, comparing the area calculated above vs. the area under the "perfect" curve.
        # area_normalised = area / calculate_maximum_area(no_snippets)
        #
        # if area_normalised >= self.patch_type_threshold:
        #     return PatchTypes.EARLY_GAIN
        #
        # return PatchTypes.GRADUAL_INCREASE
    
    
    def _get_patch_judgements(self):
        """
        Returns patch judgements from the TREC QREL file.
        """
        results_len = self._search_context.get_current_results_length()
        results_list = self._search_context.get_current_results()
        goto_depth = self.viewport_size
        
        if results_len < goto_depth:  # Sanity check -- what if the number of results is super small?
            goto_depth = results_len
        
        # List of our judgements.
        judgements = []
        
        # Obtain a list of previously examined snippet docids from the search context for the search session.
        # This probably should be refactored in the future, so that the objects can be directly compared, not the docids.
        previously_examined_snippets = [snippet.doc_id for snippet in self._search_context.get_all_examined_snippets()]
        
        for i in range(0, goto_depth):
            snippet = Document(results_list[i].whooshid, results_list[i].title, results_list[i].summary, results_list[i].docid)
            judgement = self._qrel_data_handler.get_value_fallback(self._search_context.topic.id, results_list[i].docid)
            
            if judgement is None:  # Should not happen with a fallback topic; sanity check
                judgement = 0
            elif judgement > 1:
                judgement = 1  # Easier to assume binary judgement assessments for now.
            
            # If we enter this conditional statement, novel snippets is enabled,
            #and the snippet has been previously seen. We don't consider this useful.
            if self.novel_snippets_only and results_list[i].docid in previously_examined_snippets:
                judgement = 0
            
            judgements.append(judgement)
        
        return judgements
    
    
    def _set_query_patch_type(self, patch_type):
        """
        Gets the current query from the search context, and adds the computed patch type to it.
        """
        query_object = self._search_context.get_last_query()
        setattr(query_object, 'patch_type', patch_type)
    
    
    @abc.abstractmethod
    def is_serp_attractive(self):
        """
        Abstract method that is used to determine if the SERP should be considered attractive or not.
        This is an abstract method; extend this class and override this abstract definition
        to implement this functionality.
        """
        raise NotImplementedError("You cannot call is_serp_attractive() from the base SERP impression class.")