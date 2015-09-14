import re
import math
import collections

def tokeniser(_str, stopwords=['and', 'for', 'if', 'the', 'then', 'be', 'is', 'are', 'will', 'in', 'it', 'to', 'that']):
    """
    Given an input string and list of stopwords, returns a dictionary of frequency occurrences for terms in the given input string.
    From https://gist.github.com/mrorii/961963
    """
    tokens = collections.defaultdict(lambda: 0.)
    
    for m in re.finditer(r"(\w+)", _str, re.UNICODE):
        m = m.group(1).lower()
        
        if len(m) < 2:
            continue
            
        if m in stopwords:
            continue
        
        tokens[m] += 1
        
    return tokens

def kl_divergence(_s, _t, stopwords=['and', 'for', 'if', 'the', 'then', 'be', 'is', 'are', 'will', 'in', 'it', 'to', 'that']):
    """
    An implementation of Kullback-Leibler divergence for comparing two strings (documents).
    From https://gist.github.com/mrorii/961963
    """
    _s = tokeniser(_s)
    _t = tokeniser(_t)
    
    if (len(_s) == 0):
        return 1e33
 
    if (len(_t) == 0):
        return 1e33
 
    ssum = 0. + sum(_s.values())
    slen = len(_s)
 
    tsum = 0. + sum(_t.values())
    tlen = len(_t)
 
    vocabdiff = set(_s.keys()).difference(set(_t.keys()))
    lenvocabdiff = len(vocabdiff)
 
    """ epsilon """
    epsilon = min(min(_s.values())/ssum, min(_t.values())/tsum) * 0.001
 
    """ gamma """
    gamma = 1 - lenvocabdiff * epsilon
 
    # print "_s: %s" % _s
    # print "_t: %s" % _t
 
    """ Check if distribution probabilities sum to 1"""
    sc = sum([v/ssum for v in _s.itervalues()])
    st = sum([v/tsum for v in _t.itervalues()])
 
    if sc < 9e-6:
        print "Sum P: %e, Sum Q: %e" % (sc, st)
        print "*** ERROR: sc does not sum up to 1. Bailing out .."
        sys.exit(2)
    if st < 9e-6:
        print "Sum P: %e, Sum Q: %e" % (sc, st)
        print "*** ERROR: st does not sum up to 1. Bailing out .."
        sys.exit(2)
 
    div = 0.
    for t, v in _s.iteritems():
        pts = v / ssum
 
        ptt = epsilon
        if t in _t:
            ptt = gamma * (_t[t] / tsum)
 
        ckl = (pts - ptt) * math.log(pts / ptt)
 
        div +=  ckl
 
    return div

