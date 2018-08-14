#
# Whoosh Interface with diversification!
# Taken from the SIGIR 2018 folder.
# 
# Author: David Maxwell and Leif Azzopardi
# Date: 2018-08-14
#

import copy
from simiir.search_interfaces.whoosh_interface import WhooshSearchInterface
from ifind.seeker.trec_diversity_qrel_handler import EntityQrelHandler

class WhooshDiversifiedInterface(WhooshSearchInterface):
    
    def __init__(self, whoosh_index_dir, qrels_diversity_file, to_rank=30, lam=1.0, model=2, implicit_or=True, pval=None, frag_type=2, frag_size=2, frag_surround=40, host=None, port=0):
        super(WhooshDiversifiedInterface, self).__init__(whoosh_index_dir, model, implicit_or, pval, frag_type, frag_size, frag_surround, host, port)
        self._diversity_qrels = EntityQrelHandler(qrels_diversity_file)
        self._to_rank = to_rank
        self._lam = lam
    
    def issue_query(self, query, top=100):
        """
        Allows one to issue a query to the underlying search engine. Takes an ifind Query object.
        Also applies diversification to the results before returning them.
        Doesn't cache the diversified results; a limitation of the ifind caching library means that
        a diversified/non-diversified set of results cannot be cached.
        """
        query.top = top
        response = self._engine.search(query)
        
        # Diversify the results.
        response = self.diversify_results(response, query.topic.id, to_rank=self._to_rank, lam=self._lam)
        
        self._last_query = query
        self._last_response = response
        return response
    
    # Copied the diversity functions in below, made them class members.
    
    @staticmethod
    def convert_results_to_list(results, deep_copy=True):
        """
        Given a Whoosh results object, converts it to a list and returns that list.
        Useful, as the Whoosh results object does not permit reassignment of Hit objects.
        Note that if deep_copy is True, a deep copy of the list is returned.
        """
        results_list = []
    
        for hit in results:
            if deep_copy:
                results_list.append(copy.copy(hit))
                continue
        
            results_list.append(hit)
    
        return results_list
        
    @staticmethod
    def get_highest_score_index(results_list):
        """
        Given a list of results, returns the index of the hit with the highest score.
        Simple find the maximum algorithm stuff going on here.
        """
        highest_score = 0.0
        highest_index = 0
        index = 0
    
        for hit in results_list:
            if hit.score > highest_score:
                highest_score = hit.score
                highest_index = index
        
            index = index + 1
    
        return highest_index

    @staticmethod
    def get_new_entities(observed_entities, document_entities):
        """
        Given a list of previously seen entities, and a list of document entities, returns
        a list of entities in the document which have not yet been previously seen.
        """
        return list(set(document_entities) - set(observed_entities))


    # def get_existing_entities(observed_entities, document_entities):
    #     """
    #     Given a list of previously seen entities, and a list of document entities, returns
    #     the intersection of the two lists -- i.e. the entities that have already been seen.
    #     """
    #     return list(set(observed_entities) & set(document_entities))

    
    def get_observed_entities_for_list(self, topic, rankings_list):
        """
        Given a list of Whoosh Hit objects, returns a list of the different entities that are mentioned in them.
        """
        observed_entities = []
    
        for hit in rankings_list:
            docid = hit.docid
        
            entities = self._diversity_qrels.get_mentioned_entities_for_doc(topic, docid)
            new_entities = WhooshDiversifiedInterface.get_new_entities(observed_entities, entities)
        
            observed_entities = observed_entities + new_entities
    
        return observed_entities


    def diversify_results(self, results, topic, to_rank=30, lam=1.0):
        """
        The diversification algorithm.
        Given a ifind results object, returns a re-ranked list, with more diverse content at the top.
        By diverse, we mean a selection of documents discussing a wider range of identified entities.
        """

        results_len = len(results.results)
        #results_len = results.scored_length()  # Doing len(results) returns the number of hits, not the top k.
        #print(results)
        # Simple sanity check -- no results? Can't diversify anything!
        if results_len == 0:
            return results
    
        # Before diversifying, check -- are there enough results to go to to_rank?
        # If not, change to_rank to the length of the results we have.
        if to_rank is None:
            to_rank = results_len
    
        # Not enough results to get to to_rank? Change the to_rank cap to the results length.
        if results_len < to_rank:
            to_rank = results_len
    
        # Check that lambda is a float in case of floating point calculations...
        if type(lam) != float:
            lam = float(lam)
    
        ############################
        ### Main algorithm below ###
        ############################
        observed_entities = []  # What entities have been previously seen? This list holds them.
    
        # As the list of results is probably larger than the depth we re-rank to, take a slice.
        # This is our original list of results that we'll be modifiying and popping from.
        old_rankings = results.results[:to_rank]
    
        # For our new rankings, start with the first document -- this won't change.
        # This list will be populated as we iterate through the other rankings list.
        new_rankings = [old_rankings.pop(0)]
    
        for i in range(1, to_rank):
            observed_entities = self.get_observed_entities_for_list(topic, new_rankings)
        
            for j in range(0, len(old_rankings)):
                docid = old_rankings[j].docid
                entities = self._diversity_qrels.get_mentioned_entities_for_doc(topic, docid)
                new_entities = WhooshDiversifiedInterface.get_new_entities(observed_entities, entities)
                #seen_entities = get_existing_entities(self._diversity_qrels, observed_entities, entities)
            
                old_rankings[j].score = old_rankings[j].score + (lam * len(new_entities))
            
            # Sort the list in reverse order, so the highest score is first. Then pop from old, push to new.
            old_rankings.sort(key=lambda x: x.score, reverse=True)
            new_rankings.append(old_rankings.pop(0))
    
        results.results = new_rankings + results.results[to_rank:]
        return results