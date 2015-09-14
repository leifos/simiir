# Enumerators for the different actions that can be performed.
# Solution from: http://stackoverflow.com/a/2182437
# Why? Encourages consistency. No typos. It either exists or it does not.

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        
        raise AttributeError

Actions = Enum(['QUERY', 'SERP', 'SNIPPET', 'DOC', 'MARK'])