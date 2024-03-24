# NCD Module - Asthma Model
The repository for the WHO NCD Asthma Model.

**Warning** - These models are still being refined, and there may be changes to the methods, the interpretation of the methods, and the results.

## General Notes on Modelling, Appendix 3, Notation, Nomenclature
### Nomenclature and Formatting in this document
This documentation is referring to state transition models.
State transition models have states, and transitions between those states.
States have a name e.g. `Healthy` or `Diseased` or `Deceased`. 
When we talk about the number of people in a state, we will refer to the "stock" of a state, or the "balance" of a state.
Sometimes, we might slip up and refer to a state as a node.
These mean the same thing.

Transitions describe moving from one state (the "source state") to another state (the "target state").
We will write about specific transitions by noting the source state and the target state, separated by an arrow e.g. `Healthy -> Diseased` or `Diseased -> Deceased`.
When we talk about the number of people moving between states (through a transition), we will refer to the "flow" between states.
Sometimes, we might slip up and refer to a transition as an edge, or a link.
These all mean the same thing.

### Appendix 3 uses generalized - not incremental - cost-effectiveness
The results for Appendix 3 use "generalized cost-effectiveness" methods.
The key result is "cost-effectiveness", which is just a measure of efficiency: how many dollars do you spend to get one unit of effect?
In particular, we talk about dollars per DALY averted, or dollars per Healthy life year gained.
When we talk about cost, we're talking about the difference in costs between two scenarios.
Similarly, when we talk about effects, we're talking about the difference in effects between two scenarios.
The first scenario is called the "Null Scenario". 
The second scenario is called the "Scale-up Scenario".
The first scenario is hypothetical and pessimistic, and imagines a world where treatments for a specific disease didn't even exist. 
The second scenario is hypothetical and ambitious, and imagines a world where treatments for a specific disease reached nearly everyone who needed them.
Therefore, the difference between these scenarios is intended to compare the best scenario (near universal coverage) with the worst scenario (complete absence of coverage), and tries to ignore the situation of "where a country is right now".
This is very different from conventional "incremental cost-effectiveness" methods, which typically compare "where you are now", with "where you are now + a little bit more of an intervention".
Therefore, comparing the results from Appendix 3 with other analyses is not advised.
The results from Appendix 3 are intended to serve as general, high-level, normative guidance. 
Further analysis should occur at with the countries specific needs in mind.

### Appendix 3 Key Assumptions
- Start Year: 2019
- End Year: 2119
- Coverage Rate: 95%
- Null Coverage Rate: 0%
- Discounting on Effects? No
- Discounting on Costs? Yes
