from simiir.serp_impressions import PatchTypes, SERPImpression
from simiir.serp_impressions.base_serp_impression import BaseSERPImpression

class SimpleSERPImpression(BaseSERPImpression):
    """
    A simple approach to SERP impression judging.
    The de facto approach used in prior simulations; assume it's worth examining. Always return True.
    """
    def __init__(self, search_context, topic):
        super(SimpleSERPImpression, self).__init__(search_context, topic)
    
    def initialise(self):
        """
        No prior initialisations are required.
        """
        pass
    
    def get_impression(self):
        """
        Simplistic approach; always assume that the SERP has some degree of relevancy, thus the searcher enters the SERP to judge snippets.
        """
        return SERPImpression(True, PatchTypes.UNDEFINED)