import abc
import numpy
from numpy import trapz
from simiir.serp_impressions import PatchTypes

class BaseSERPImpression(object):
    """
    Base class for SERP impression judging.
    Contains two series of abstract methods (calculate() and is_attractive()) for judging the attractiveness of a SERP.
    Also includes some simple logic to judge the "type" of "patch" a given SERP is (judge_patch()).
    For more information on patch types, refer to Stephens and Krebs (Foraging Theory, 1986), Section 8.3.
    """
    def __init__(self, search_context, topic, dcg_discount=0.5, patch_type_threshold=0.6):
        """
        Instantiates a SERP impression object.
        """
        self._search_context = search_context
        self._topic = topic
        self._dcg_discount = dcg_discount
        self._patch_type_threshold = patch_type_threshold
    
    def __calculate_maximum_area(self, snippet_judgements_length):
        print [1] * snippet_judgements_length
    
    def _calculate_patch_type(self, snippet_judgements=None):
        """
        Given a series of snippet judgements (as an ordered list, with 1=relevant, 0=non-relevant), calculates the patch type, as per
        Stephen and Krebs (1986), Section 8.3. To calculate how good the SERP is judged to appear, the area under the DCG curve is calculated.
        This is done via integration along the y axis using the composite trapezoidal rule.
        
        If the normalised area (with respect to a perfect DCG curve, where gain is extracted from every document) is equal to or above
        a given threshold, the patch is considered a high yielding patch (early on). Otherwise, we consider it to be a gradually yielding patch.
        """
        def maximum_area(snippet_judgements_length):
            perfect_judgements = [1] * snippet_judgements_length
            cumulative_perfect_judgements = numpy.cumsum(perfect_judgements)
            return float(trapz(cumulative_perfect_judgements, dx=snippet_judgements_length))
        
        if snippet_judgements is None or len(snippet_judgements) == 1:
            return PatchTypes.UNDEFINED
        
        no_snippets = len(snippet_judgements)
        
        # Calculate the DCG at each rank, with the dcg threshold specified.
        dcg_values = []
        
        for i in range(0, len(snippet_judgements)):
            dcg = snippet_judgements[i] * (1.0/(i+1)**self._dcg_discount)
            dcg_values.append(dcg)
        
        cumulative = numpy.cumsum(dcg_values)
        area = trapz(cumulative, dx=no_snippets)
        
        area_normalised = area / maximum_area(no_snippets)
        
        if area_normalised >= self._patch_type_threshold:
            return PatchTypes.EARLY_GAIN
        
        return PatchTypes.GRADUAL_INCREASE
    
    @abc.abstractmethod
    def initialise(self):
        """
        Abstract method -- used for more complex impression judging approaches for prior calculations/instantiations.
        """
        raise NotImplementedError("Cannot call an abstract method (SERP Impression/initialise).")
    
    @abc.abstractmethod
    def get_impression(self):
        """
        Abstract method -- used to return the overall judgement of the SERP (boolean) and a judgement of the SERP patch type.
        """
        raise NotImplementedError("Cannot call an abstract method (SERP Impression/get_impression).")