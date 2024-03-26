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

# Test Results

| Country | Scenario  | STATUS_CODE | HYL          |
|---------|-----------|-------------|--------------|
| AFG | baseline | 200 | 45,709,103 |
| AFG | null | 200 | 45,707,405 |
| AFG | cr1 | 200 | 45,727,239 |
| AFG | cr3 | 200 | 45,721,517 |
| DZA | baseline | 200 | 50,352,632 |
| DZA | null | 200 | 50,351,006 |
| DZA | cr1 | 200 | 50,370,000 |
| DZA | cr3 | 200 | 50,364,520 |
| AGO | baseline | 200 | 38,568,754 |
| AGO | null | 200 | 38,567,245 |
| AGO | cr1 | 200 | 38,584,875 |
| AGO | cr3 | 200 | 38,579,789 |
| ARG | baseline | 200 | 51,272,740 |
| ARG | null | 200 | 51,268,896 |
| ARG | cr1 | 200 | 51,313,815 |
| ARG | cr3 | 200 | 51,300,856 |
| BGD | baseline | 200 | 194,215,570 |
| BGD | null | 200 | 194,212,506 |
| BGD | cr1 | 200 | 194,248,308 |
| BGD | cr3 | 200 | 194,237,979 |
| BRA | baseline | 200 | 243,399,740 |
| BRA | null | 200 | 243,390,379 |
| BRA | cr1 | 200 | 243,499,770 |
| BRA | cr3 | 200 | 243,468,210 |
| BFA | baseline | 200 | 25,040,404 |
| BFA | null | 200 | 25,039,614 |
| BFA | cr1 | 200 | 25,048,837 |
| BFA | cr3 | 200 | 25,046,176 |
| BDI | baseline | 200 | 14,154,989 |
| BDI | null | 200 | 14,154,294 |
| BDI | cr1 | 200 | 14,162,411 |
| BDI | cr3 | 200 | 14,160,069 |
| CMR | baseline | 200 | 30,831,705 |
| CMR | null | 200 | 30,830,844 |
| CMR | cr1 | 200 | 30,840,908 |
| CMR | cr3 | 200 | 30,838,005 |
| CAF | baseline | 200 | 6,184,067 |
| CAF | null | 200 | 6,183,806 |
| CAF | cr1 | 200 | 6,186,857 |
| CAF | cr3 | 200 | 6,185,976 |
| TCD | baseline | 200 | 19,512,539 |
| TCD | null | 200 | 19,512,030 |
| TCD | cr1 | 200 | 19,517,986 |
| TCD | cr3 | 200 | 19,516,268 |
| CHN | baseline | 200 | 1,688,025,721 |
| CHN | null | 200 | 1,687,999,693 |
| CHN | cr1 | 200 | 1,688,303,855 |
| CHN | cr3 | 200 | 1,688,216,102 |
| COL | baseline | 200 | 59,364,127 |
| COL | null | 200 | 59,362,496 |
| COL | cr1 | 200 | 59,381,551 |
| COL | cr3 | 200 | 59,376,053 |
| COD | baseline | 200 | 107,368,368 |
| COD | null | 200 | 107,364,347 |
| COD | cr1 | 200 | 107,411,336 |
| COD | cr3 | 200 | 107,397,780 |
| CIV | baseline | 200 | 31,063,989 |
| CIV | null | 200 | 31,062,830 |
| CIV | cr1 | 200 | 31,076,374 |
| CIV | cr3 | 200 | 31,072,466 |
| DOM | baseline | 200 | 12,459,168 |
| DOM | null | 200 | 12,458,698 |
| DOM | cr1 | 200 | 12,464,195 |
| DOM | cr3 | 200 | 12,462,609 |
| ECU | baseline | 200 | 22,905,464 |
| ECU | null | 200 | 22,905,149 |
| ECU | cr1 | 200 | 22,908,827 |
| ECU | cr3 | 200 | 22,907,766 |
| EGY | baseline | 200 | 125,287,023 |
| EGY | null | 200 | 125,282,606 |
| EGY | cr1 | 200 | 125,334,221 |
| EGY | cr3 | 200 | 125,319,330 |
| ERI | baseline | 200 | 4,081,243 |
| ERI | null | 200 | 4,081,025 |
| ERI | cr1 | 200 | 4,083,570 |
| ERI | cr3 | 200 | 4,082,836 |
| ETH | baseline | 200 | 136,038,975 |
| ETH | null | 200 | 136,034,359 |
| ETH | cr1 | 200 | 136,088,301 |
| ETH | cr3 | 200 | 136,072,739 |
| GMB | baseline | 200 | 2,991,001 |
| GMB | null | 200 | 2,990,902 |
| GMB | cr1 | 200 | 2,992,057 |
| GMB | cr3 | 200 | 2,991,724 |
| GHA | baseline | 200 | 37,198,081 |
| GHA | null | 200 | 37,197,111 |
| GHA | cr1 | 200 | 37,208,451 |
| GHA | cr3 | 200 | 37,205,179 |
| GTM | baseline | 200 | 20,658,979 |
| GTM | null | 200 | 20,658,484 |
| GTM | cr1 | 200 | 20,664,270 |
| GTM | cr3 | 200 | 20,662,601 |
| GIN | baseline | 200 | 15,268,244 |
| GIN | null | 200 | 15,267,630 |
| GIN | cr1 | 200 | 15,274,806 |
| GIN | cr3 | 200 | 15,272,736 |
| GNB | baseline | 200 | 2,333,250 |
| GNB | null | 200 | 2,333,165 |
| GNB | cr1 | 200 | 2,334,161 |
| GNB | cr3 | 200 | 2,333,873 |
| HTI | baseline | 200 | 12,689,150 |
| HTI | null | 200 | 12,688,263 |
| HTI | cr1 | 200 | 12,698,625 |
| HTI | cr3 | 200 | 12,695,636 |
| IND | baseline | 200 | 1,602,828,928 |
| IND | null | 200 | 1,602,777,786 |
| IND | cr1 | 200 | 1,603,375,415 |
| IND | cr3 | 200 | 1,603,202,995 |
| IDN | baseline | 200 | 314,764,487 |
| IDN | null | 200 | 314,753,829 |
| IDN | cr1 | 200 | 314,878,369 |
| IDN | cr3 | 200 | 314,842,439 |
| IRN | baseline | 200 | 100,227,010 |
| IRN | null | 200 | 100,223,594 |
| IRN | cr1 | 200 | 100,263,511 |
| IRN | cr3 | 200 | 100,251,995 |
| IRQ | baseline | 200 | 50,074,605 |
| IRQ | null | 200 | 50,072,971 |
| IRQ | cr1 | 200 | 50,092,064 |
| IRQ | cr3 | 200 | 50,086,556 |
| JOR | baseline | 200 | 12,722,232 |
| JOR | null | 200 | 12,721,743 |
| JOR | cr1 | 200 | 12,727,465 |
| JOR | cr3 | 200 | 12,725,814 |
| KAZ | baseline | 200 | 22,295,533 |
| KAZ | null | 200 | 22,295,183 |
| KAZ | cr1 | 200 | 22,299,275 |
| KAZ | cr3 | 200 | 22,298,094 |
| KEN | baseline | 200 | 60,295,769 |
| KEN | null | 200 | 60,293,789 |
| KEN | cr1 | 200 | 60,316,921 |
| KEN | cr3 | 200 | 60,310,247 |
| MDG | baseline | 200 | 32,020,544 |
| MDG | null | 200 | 32,018,132 |
| MDG | cr1 | 200 | 32,046,309 |
| MDG | cr3 | 200 | 32,038,180 |
| MWI | baseline | 200 | 22,466,909 |
| MWI | null | 200 | 22,465,921 |
| MWI | cr1 | 200 | 22,477,470 |
| MWI | cr3 | 200 | 22,474,138 |
| MYS | baseline | 200 | 38,594,116 |
| MYS | null | 200 | 38,593,189 |
| MYS | cr1 | 200 | 38,604,015 |
| MYS | cr3 | 200 | 38,600,892 |
| MLI | baseline | 200 | 24,867,467 |
| MLI | null | 200 | 24,866,826 |
| MLI | cr1 | 200 | 24,874,310 |
| MLI | cr3 | 200 | 24,872,151 |
| MEX | baseline | 200 | 147,926,773 |
| MEX | null | 200 | 147,923,558 |
| MEX | cr1 | 200 | 147,961,134 |
| MEX | cr3 | 200 | 147,950,293 |
| MAR | baseline | 200 | 42,373,038 |
| MAR | null | 200 | 42,371,738 |
| MAR | cr1 | 200 | 42,386,930 |
| MAR | cr3 | 200 | 42,382,547 |
| MOZ | baseline | 200 | 36,021,943 |
| MOZ | null | 200 | 36,020,112 |
| MOZ | cr1 | 200 | 36,041,505 |
| MOZ | cr3 | 200 | 36,035,333 |
| MMR | baseline | 200 | 62,440,143 |
| MMR | null | 200 | 62,438,856 |
| MMR | cr1 | 200 | 62,453,889 |
| MMR | cr3 | 200 | 62,449,552 |
| NPL | baseline | 200 | 34,271,950 |
| NPL | null | 200 | 34,271,548 |
| NPL | cr1 | 200 | 34,276,241 |
| NPL | cr3 | 200 | 34,274,887 |
| NER | baseline | 200 | 28,423,766 |
| NER | null | 200 | 28,422,846 |
| NER | cr1 | 200 | 28,433,600 |
| NER | cr3 | 200 | 28,430,497 |
| NGA | baseline | 200 | 240,643,780 |
| NGA | null | 200 | 240,633,414 |
| NGA | cr1 | 200 | 240,754,557 |
| NGA | cr3 | 200 | 240,719,606 |
| PAK | baseline | 200 | 267,437,328 |
| PAK | null | 200 | 267,433,013 |
| PAK | cr1 | 200 | 267,483,441 |
| PAK | cr3 | 200 | 267,468,892 |
| PER | baseline | 200 | 43,281,751 |
| PER | null | 200 | 43,281,101 |
| PER | cr1 | 200 | 43,288,688 |
| PER | cr3 | 200 | 43,286,499 |
| PHL | baseline | 200 | 130,197,055 |
| PHL | null | 200 | 130,191,716 |
| PHL | cr1 | 200 | 130,254,114 |
| PHL | cr3 | 200 | 130,236,111 |
| RUS | baseline | 200 | 166,446,924 |
| RUS | null | 200 | 166,443,248 |
| RUS | cr1 | 200 | 166,486,199 |
| RUS | cr3 | 200 | 166,473,808 |
| RWA | baseline | 200 | 14,783,244 |
| RWA | null | 200 | 14,781,854 |
| RWA | cr1 | 200 | 14,798,100 |
| RWA | cr3 | 200 | 14,793,413 |
| SLE | baseline | 200 | 9,523,824 |
| SLE | null | 200 | 9,523,503 |
| SLE | cr1 | 200 | 9,527,254 |
| SLE | cr3 | 200 | 9,526,172 |
| ZAF | baseline | 200 | 66,698,388 |
| ZAF | null | 200 | 66,695,162 |
| ZAF | cr1 | 200 | 66,732,868 |
| ZAF | cr3 | 200 | 66,721,989 |
| LKA | baseline | 200 | 24,902,994 |
| LKA | null | 200 | 24,901,885 |
| LKA | cr1 | 200 | 24,914,841 |
| LKA | cr3 | 200 | 24,911,103 |
| SDN | baseline | 200 | 51,272,487 |
| SDN | null | 200 | 51,270,018 |
| SDN | cr1 | 200 | 51,298,878 |
| SDN | cr3 | 200 | 51,290,552 |
| TJK | baseline | 200 | 11,386,252 |
| TJK | null | 200 | 11,386,042 |
| TJK | cr1 | 200 | 11,388,497 |
| TJK | cr3 | 200 | 11,387,789 |
| TZA | baseline | 200 | 70,421,136 |
| TZA | null | 200 | 70,416,189 |
| TZA | cr1 | 200 | 70,473,996 |
| TZA | cr3 | 200 | 70,457,318 |
| THA | baseline | 200 | 80,835,063 |
| THA | null | 200 | 80,832,023 |
| THA | cr1 | 200 | 80,867,540 |
| THA | cr3 | 200 | 80,857,294 |
| TGO | baseline | 200 | 9,720,792 |
| TGO | null | 200 | 9,720,378 |
| TGO | cr1 | 200 | 9,725,220 |
| TGO | cr3 | 200 | 9,723,823 |
| TUR | baseline | 200 | 95,533,008 |
| TUR | null | 200 | 95,527,406 |
| TUR | cr1 | 200 | 95,592,865 |
| TUR | cr3 | 200 | 95,573,979 |
| UGA | baseline | 200 | 51,327,486 |
| UGA | null | 200 | 51,324,580 |
| UGA | cr1 | 200 | 51,358,537 |
| UGA | cr3 | 200 | 51,348,740 |
| UKR | baseline | 200 | 49,788,460 |
| UKR | null | 200 | 49,787,153 |
| UKR | cr1 | 200 | 49,802,429 |
| UKR | cr3 | 200 | 49,798,022 |
| UZB | baseline | 200 | 39,408,408 |
| UZB | null | 200 | 39,407,291 |
| UZB | cr1 | 200 | 39,420,340 |
| UZB | cr3 | 200 | 39,416,576 |
| VNM | baseline | 200 | 111,504,825 |
| VNM | null | 200 | 111,501,148 |
| VNM | cr1 | 200 | 111,544,115 |
| VNM | cr3 | 200 | 111,531,719 |
