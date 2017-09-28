import abc
import numpy
from simiir.search_interfaces import Document
from simiir.serp_impressions import PatchTypes
from simiir.utils.data_handlers import get_data_handler

class SimpleSERPImpression(object):
    """
    A simple approach to SERP impression judging.
    The de facto approach used in prior simulations; assume it's worth examining. Always return True.
    Also includes code to judge the patch type, a different thing from determining if the patch should be entered or not.
    """
    def __init__(self, search_context, topic, qrel_file, host=None, port=None, dcg_discount=0.5, patch_type_threshold=0.6, viewport_size=10):
        self._search_context = search_context
        self._topic = topic
        
        self._dcg_discount = dcg_discount
        self._patch_type_threshold = patch_type_threshold
        self._viewport_size = viewport_size
        
        self._qrel_data_handler = get_data_handler(filename=qrel_file, host=host, port=port, key_prefix='serpimpressions')
    
    
    def _calculate_patch_type(self, snippet_judgements=None):
        """
        Given a series of snippet judgements (as an ordered list, with 1=relevant, 0=non-relevant), calculates the patch type, as per
        Stephen and Krebs (1986), Section 8.3. To calculate how good the SERP is judged to appear, the area under the DCG curve is calculated.
        This is done via integration along the y axis using the composite trapezoidal rule.
        
        If the normalised area (with respect to a perfect DCG curve, where gain is extracted from every document) is equal to or above
        a given threshold, the patch is considered a high yielding patch (early on). Otherwise, we consider it to be a gradually yielding patch.
        
        This method can probably be spun out into a separate component in the future; for now, a single approach is sufficient.
        """
        def calculate_maximum_area(snippet_judgements_length):
            """
            Given a length parameter, returns the maximum area under the curve if all documents up to
            length snippet_judgements_length are judged to be relevant.
            """
            perfect_judgements = [1] * snippet_judgements_length
            cumulative_perfect_judgements = numpy.cumsum(perfect_judgements)
            return float(numpy.trapz(cumulative_perfect_judgements, dx=snippet_judgements_length))
        
        
        if snippet_judgements is None or len(snippet_judgements) == 1:
            return PatchTypes.UNDEFINED
        
        no_snippets = len(snippet_judgements)
        
        # Calculate the DCG at each rank, with the DCG threshold specified.
        dcg_values = []
        
        for i in range(0, len(snippet_judgements)):
            dcg = snippet_judgements[i] * (1.0/(i+1)**self._dcg_discount)
            dcg_values.append(dcg)
        
        cumulative = numpy.cumsum(dcg_values)
        area = numpy.trapz(cumulative, dx=no_snippets)
        
        # Produce a ratio, comparing the area calculated above vs. the area under the "perfect" curve.
        area_normalised = area / calculate_maximum_area(no_snippets)
        
        if area_normalised >= self._patch_type_threshold:
            return PatchTypes.EARLY_GAIN
        
        return PatchTypes.GRADUAL_INCREASE
    
    
    def _get_patch_judgements(self):
        """
        Returns patch judgements from the TREC QREL file.
        """
        results_len = self._search_context.get_current_results_length()
        results_list = self._search_context.get_current_results()
        goto_depth = self._viewport_size
        
        if results_len < goto_depth:  # Sanity check -- what if the number of results is super small?
            goto_depth = results_len
        
        judgements = []
        
        for i in range(0, goto_depth):
            snippet = Document(results_list[i].whooshid, results_list[i].title, results_list[i].summary, results_list[i].docid)
            judgement = self._qrel_data_handler.get_value_fallback(self._topic.id, results_list[i].docid)
            
            if judgement is None:  # Should not happen with a fallback topic; sanity check
                judgement = 0
            elif judgement > 1:
                judgement = 1  # Easier to assume binary judgement assessments for now.
            
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
        Determines whether the SERP is attractive.
        As this is the SimpleSERPImpression, the SERP is always considered attractive.
        This will mean at least one snippet will be examined by the simulated user.
        
        For more complex SERP examination strategies, override this method.
        """
        patch_judgements = self._get_patch_judgements()  # We don't have a means of working out judgements for
                                                          # determining patch type, so fall back to TREC judgements.
        patch_type = self._calculate_patch_type(patch_judgements)
        self._set_query_patch_type(patch_type)
        
        return True