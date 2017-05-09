from loggers import Actions
from lxml.html.clean import Cleaner
from utils import difference_methods
from stopping_decision_makers.base_decision_maker import BaseDecisionMaker

class DifferenceDecisionMaker(BaseDecisionMaker):
    """
    A concrete implementation of a decision maker.
    Using KL-Divergence to determine how "different" snippets/documents are to one another, makes a decision what to do next.
    """
    def __init__(self, search_context, logger, stopword_file, threshold, decision_maker=1, nonrel_only=False, query_based=True, vocab_file=None, alpha=0.5):
        super(DifferenceDecisionMaker, self).__init__(search_context, logger)
        
        self.__stopwords = self.__get_stopwords_list(stopword_file)
        self.__threshold = threshold
        self.__query_based = query_based  # Determines if the decision maker is query-based (i.e. only snippets/documents in a SERP) or session-based (i.e. all snippets/documents observed through a search session).
        self.__nonrel_only = nonrel_only
        
        decision_maker = decision_maker.lower()
        
        if decision_maker == 'kl':  # KL-Divergence
            self.__decision_maker = difference_methods.KLDifference(stopword_file=stopword_file, vocab_file=vocab_file, alpha=alpha)
            self.__comparator = lambda score, threshold: score < threshold
        elif decision_maker == 'term_overlap':  # Default to the TermOverlapDecisionMaker
            self.__decision_maker = difference_methods.TermOverlapDifference(stopword_file=stopword_file, vocab_file=vocab_file)
            self.__comparator = lambda score, threshold: score > threshold
        else:
            raise ValueError("Invalid decision maker type specified.")
        
        
    def decide(self):
        """
        Determines whether the user should proceed to examine the subsequent snippet, or stop and issue a new query.
        """
        seen_text = ""
        existing = []

        if self.__query_based:  # If this is query-based, we look at only snippets that were examined in the current query.
            existing = self._search_context.get_examined_snippets()
        else:
            existing = self._search_context.get_all_examined_snippets()

        if self.__nonrel_only:  # Filter to only nonrelevant documents using a list comprehension.
            existing = [snippet for snippet in existing if snippet.judgment < 1]

        #if zero or one snippets have been examined, then move to the next snippet.
        if len(existing) <= 1:
            return Actions.SNIPPET

        current_snippet = existing[-1]
        remaining_snippets = existing[:-1]
        
        current_snippet.title = current_snippet.title.encode('utf-8', errors='ignore')
        current_snippet.content = current_snippet.content.encode('utf-8', errors='ignore')
                
        new_text = "{0} {1}".format(current_snippet.title, self.__clean_markup(current_snippet.content))

        for snippet in remaining_snippets:
            seen_text = ''.join([i if ord(i) < 128 else ' ' for i in seen_text])
            snippet.title = ''.join([i if ord(i) < 128 else ' ' for i in snippet.title])
            snippet.content = ''.join([i if ord(i) < 128 else ' ' for i in snippet.content])
            
            seen_text = "{0} {1} {2}".format(seen_text, snippet.title, self.__clean_markup(snippet.content))
        
        topic = self._search_context.get_topic()
        seen_text = "{0} {1} {2}".format(seen_text, topic.title, self.__clean_markup(snippet.content))
        seen_text = "{0} {1} {2}".format(seen_text, topic.content, self.__clean_markup(snippet.content))

        score = self.__decision_maker.difference(new_text,seen_text)
        #print "diff", score
        #print "SEEN:", seen_text
        #print "NEW:", new_text
        #print
        #raw_input()

        if self.__comparator(score, self.__threshold):
        # if the new text is too similar to the seen text then move to the next query
            return Actions.QUERY  # Too similar?
        # else move to the next snippet.
        return Actions.SNIPPET  #  Different enough, so proceed to examine the next snippet.

    
    def __clean_markup(self, string_repr):
        """
        Given a string representation of a document or snippet, removes all HTML markup and returns it, cleaned.
        """
        if string_repr == "":
            return string_repr
        
        cleaner = Cleaner(allow_tags=[''], remove_unknown_tags=False)
        cleaned_text = cleaner.clean_html(string_repr)
        
        return cleaned_text[5:][:-6]  # Removes the extra <div>...</div> that is added
    
    def __get_stopwords_list(self, stopwords_filename):
        """
        Given the stopwords instance variable, returns a list of stopwords to use.
        Assumes that each word to be used is on a new line.
        """
        stopwords_file = open(stopwords_filename, 'r')
        stopwords = []
        
        for line in stopwords_file:
            line = line.strip()
            stopwords.append(line)
        
        stopwords_file.close()
        return stopwords