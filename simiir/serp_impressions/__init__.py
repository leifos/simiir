from simiir.utils.enum import Enum

PatchTypes = Enum(['EARLY_GAIN', 'GRADUAL_INCREASE', 'UNDEFINED'])  # As per Foraging Theory, Section 8.3 (Single Patch Type).

class SERPImpression:
    def __init__(self, impression_judgement, patch_type):
        self.impression_judgement = impression_judgement
        self.patch_type = patch_type
    
    def __repr__(self):
        return "<Impression: {impression}, Patch: {patch}>".format(impression=self.impression_judgement, patch=self.patch_type)