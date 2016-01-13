# simiir
This directory contains a number of files for running TREC based simulations.

index/ contains a whoosh index of a small portion of the TREC Aquaint index (see the https://github.com/leifos/ifind for a script for indexing TREC Aquaint)

probs/ contains pre-rolled decisions of whether a snippet is considered relevant or not (.click)
or whether a document is considered relevant or not (.mark). The probabilities are based on the values
from Smucker's paper and Maxwell and Azzopardi's paper.

qrels/ contains the TREC Aquaint relevance judgements

terms/ contains a stopword list and the background term list from the full TREC Aquaint with counts.

topics/ contains pre-processed topics from TREC Aquaint, which are given to the simulated user to perform.

