# simiir

A toolkit for simulating interactive information retrieval


## ifind
To use this toolkit you will also need to download and install:

https://github.com/leifos/ifind

Add the ifind library to your PYTHONPATH


## trec_eval

To determine the performance of the output of the simulations automatically, you will need to download trec_eval:

http://trec.nist.gov/trec_eval/

Add trec_eval to your PATH.


## simiir setup

Add simiir to your PYTHONPATH

Create a virtual environment with the packages in the requirements.txt (note it is the same as the one for ifind)


## run sample simulations

make a directory called output in example_sims

cd into the simiir directory, and run:

python run_simiir.py ../example_sims/trec_bm25_simulation.xml

or

python run_simiir.py ../example_sims/trec_pl2_simulation.xml

You will see the simulations running where the simulated users use either BM25 or PL2.

The output of the simulations will be in example_sims/output


## simulation.xml files

You will see that a simulation takes four main elements:

### output
This is where the output of the simulation is to be stored.
If you do not want (or have not installed trec_eval) then you can set trec_eval to false,
and it will not automatically evaluate the output of the simulations.


### topics
A set of sample topics have been included in example_data/topics.

You can include each topic that you would like the simulated users to undertake.


### users
A set of sample users have been created and included in example_sims/users.

You can include however many users you would like to user the searchInterface, and the topics specified.

Each of the users have been configured differently to show how the different components can be set to instantiate different simulated users.

    #### trec_user
    Submits one query, the topic title.

    Examines each snippet, and each document, and considers them relevant.

    #### fixed_depth_user

    Submits three word queries - generated from the topic description

    Examines to a fixed depth, initially set to 10.

    Each snippet that the simulated user examines, it stochastically decides whether it should examine it or not, based on the specified probabilities.

    Each document that the simulated user examines, it stochastically decides whether it should mark it as relevant or not, based on the specified probabilities.


### searchInterface
The search interface is a programmatic representation of the search interface an actual user would use.

It currently lets the simulated user do two actions: query and examine a document.

Note: the simulator acts as an broker to query and fetch documents, and controls the flow of actions, i.e.
querying, examining snippets, assessing documents, marking documents as relevant, etc.

At the moment only one search interface is specified which connects to a Whoosh Based Index of TREC documents.









