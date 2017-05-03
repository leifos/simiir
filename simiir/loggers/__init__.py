# Enumerators for the different actions that can be performed.
# Solution from: http://stackoverflow.com/a/2182437
# Why? Encourages consistency. No typos. It either exists or it does not.

from simiir.utils.enum import Enum

Actions = Enum(['QUERY', 'SERP', 'SNIPPET', 'DOC', 'MARK'])