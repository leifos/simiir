__author__ = 'leif'
import re
import abc
import sys
import math
import collections

class DifferenceHelper(object):
    """
    Abstract difference class.
    Contains helper methods for setting up - the difference() method is abstract.
    """
    def __init__(self, stopword_file=None, vocab_file=None):
        self.vocab = self.__read_vocab_dict(vocab_file)
        self.stopwords = self.__read_stopwords_list(stopword_file)
        
        if not self.stopwords:
            self.stopwords = ['and', 'for', 'if', 'the', 'then', 'be', 'is', 'are', 'will', 'in', 'it', 'to', 'that']
    
    
    def __read_stopwords_list(self, stopwords_file):
        """
        Given the stopwords instance variable, returns a list of stopwords to use.
        Assumes that each word to be used is on a new line.
        """
        stopwords = []
        if stopwords_file:
            f = open(stopwords_file, 'r')
            for line in f:
                line = line.strip()
                stopwords.append(line)

            f.close()
        return stopwords


    def __read_vocab_dict(self, vocab_file):
        """
        :param vocab_file: Given a file which is a list of (word (string) ,count (int)) pairs on newlines
        :return: a dictionary of the words and their counts
        """
        vocab = {}
        if vocab_file:
            f = open(vocab_file, 'r')
            for line in f:
                split_line=line.strip().split(',')
                term = split_line[0]
                count = int(split_line[1])
                vocab[term] = count
        return vocab


    def _tokeniser(self, _str, stopwords=['and', 'for', 'if', 'the', 'then', 'be', 'is', 'are', 'will', 'in', 'it', 'to', 'that']):
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
    
    @abc.abstractmethod
    def difference(self, new_text, seen_text):
        """
        Abstract method for determining the difference between previously seen and unseen text.
        """
        return NotImplementedError()
        

class TermOverlapDifference(DifferenceHelper):
    """
    String difference implemenattion - determines the difference between two strings by counting term overlaps.
    """
    def __init__(self, stopword_file=None, vocab_file=None):
        super(TermOverlapDifference, self).__init__(stopword_file, vocab_file)
    
    def difference(self, new_text, seen_text):
        """
        Concrete implementation - works out the term overlap between the two passed strings.
        """
        new_text = self._tokeniser(new_text)
        seen_text = self._tokeniser(seen_text)
        
        new_text_length = len(new_text)
        overlap_count = 0.0
        
        for term in new_text.keys():
            if term in seen_text.keys():
                overlap_count += 1
        
        return overlap_count / new_text_length

class KLDifference(DifferenceHelper):
    """
    Implementation of KL-Divergence for determining the difference between two texts (strings).
    """
    def __init__(self, alpha = 0.5, stopword_file=None, vocab_file=None):
        super(KLDifference, self).__init__(stopword_file, vocab_file)
        self.alpha = alpha # the mixing co-efficient
    
    
    def difference(self, new_text, seen_text):
        """
        Concrete implementation - works out the KL divergence between the two passed strings.
        """
        new_text = self._tokeniser(new_text)
        seen_text = self._tokeniser(seen_text)

        # need to mix the seen text with the background text.

        for t in seen_text:
            seen_text[t] =  seen_text[t] * self.alpha/(1-self.alpha)
        
        # dmax says: I don't understand this; and the results don't level off as well as the implementation below.
        # for t in self.vocab:
        #     if seen_text[t]:
        #         seen_text[t] = seen_text[t] + self.vocab[t]
        #     else:
        #         seen_text[t] = self.vocab[t]
        
        for t in self.vocab:
            if t in seen_text:
                seen_text[t] += 1
            else:
                seen_text[t] = 1.0
        
        return self.__kl_divergence(new_text,seen_text)
    
    
    def __kl_divergence(self,_s, _t):
        """
        An implementation of Kullback-Leibler divergence for comparing two strings (documents).
        From https://gist.github.com/mrorii/961963
        """
        stopwords = self.stopwords

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