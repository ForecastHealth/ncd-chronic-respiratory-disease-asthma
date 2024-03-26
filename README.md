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
| AFG | baseline | 200 | 45709103.10 |
| AFG | null | 200 | 45707405.86 |
| AFG | cr1 | 200 | 45727239.25 |
| AFG | cr3 | 200 | 45721517.19 |
| DZA | baseline | 200 | 50352632.10 |
| DZA | null | 200 | 50351006.67 |
| DZA | cr1 | 200 | 50370000.93 |
| DZA | cr3 | 200 | 50364520.96 |
| AGO | baseline | 200 | 38568754.23 |
| AGO | null | 200 | 38567245.56 |
| AGO | cr1 | 200 | 38584875.40 |
| AGO | cr3 | 200 | 38579789.08 |
| ARG | baseline | 200 | 51272740.81 |
| ARG | null | 200 | 51268896.92 |
| ARG | cr1 | 200 | 51313815.49 |
| ARG | cr3 | 200 | 51300856.20 |
| BGD | baseline | 200 | 194215570.31 |
| BGD | null | 200 | 194212506.55 |
| BGD | cr1 | 200 | 194248308.71 |
| BGD | cr3 | 200 | 194237979.56 |
| BRA | baseline | 200 | 243399740.40 |
| BRA | null | 200 | 243390379.27 |
| BRA | cr1 | 200 | 243499770.64 |
| BRA | cr3 | 200 | 243468210.53 |
| BFA | baseline | 200 | 25040404.09 |
| BFA | null | 200 | 25039614.88 |
| BFA | cr1 | 200 | 25048837.36 |
| BFA | cr3 | 200 | 25046176.62 |
| BDI | baseline | 200 | 14154989.11 |
| BDI | null | 200 | 14154294.46 |
| BDI | cr1 | 200 | 14162411.90 |
| BDI | cr3 | 200 | 14160069.97 |
| CMR | baseline | 200 | 30831705.49 |
| CMR | null | 200 | 30830844.21 |
| CMR | cr1 | 200 | 30840908.89 |
| CMR | cr3 | 200 | 30838005.16 |
| CAF | baseline | 200 | 6184067.12 |
| CAF | null | 200 | 6183806.01 |
| CAF | cr1 | 200 | 6186857.28 |
| CAF | cr3 | 200 | 6185976.96 |
| TCD | baseline | 200 | 19512539.97 |
| TCD | null | 200 | 19512030.26 |
| TCD | cr1 | 200 | 19517986.56 |
| TCD | cr3 | 200 | 19516268.13 |
| CHN | baseline | 200 | 1688025721.65 |
| CHN | null | 200 | 1687999693.02 |
| CHN | cr1 | 200 | 1688303855.81 |
| CHN | cr3 | 200 | 1688216102.90 |
| COL | baseline | 200 | 59364127.54 |
| COL | null | 200 | 59362496.99 |
| COL | cr1 | 200 | 59381551.22 |
| COL | cr3 | 200 | 59376053.95 |
| COD | baseline | 200 | 107368368.90 |
| COD | null | 200 | 107364347.82 |
| COD | cr1 | 200 | 107411336.89 |
| COD | cr3 | 200 | 107397780.25 |
| CIV | baseline | 200 | 31063989.59 |
| CIV | null | 200 | 31062830.61 |
| CIV | cr1 | 200 | 31076374.08 |
| CIV | cr3 | 200 | 31072466.70 |
| DOM | baseline | 200 | 12459168.60 |
| DOM | null | 200 | 12458698.19 |
| DOM | cr1 | 200 | 12464195.20 |
| DOM | cr3 | 200 | 12462609.28 |
| ECU | baseline | 200 | 22905464.06 |
| ECU | null | 200 | 22905149.31 |
| ECU | cr1 | 200 | 22908827.36 |
| ECU | cr3 | 200 | 22907766.22 |
| EGY | baseline | 200 | 125287023.80 |
| EGY | null | 200 | 125282606.91 |
| EGY | cr1 | 200 | 125334221.33 |
| EGY | cr3 | 200 | 125319330.24 |
| ERI | baseline | 200 | 4081243.53 |
| ERI | null | 200 | 4081025.73 |
| ERI | cr1 | 200 | 4083570.78 |
| ERI | cr3 | 200 | 4082836.52 |
| ETH | baseline | 200 | 136038975.53 |
| ETH | null | 200 | 136034359.44 |
| ETH | cr1 | 200 | 136088301.70 |
| ETH | cr3 | 200 | 136072739.01 |
| GMB | baseline | 200 | 2991001.82 |
| GMB | null | 200 | 2990902.98 |
| GMB | cr1 | 200 | 2992057.95 |
| GMB | cr3 | 200 | 2991724.73 |
| GHA | baseline | 200 | 37198081.73 |
| GHA | null | 200 | 37197111.28 |
| GHA | cr1 | 200 | 37208451.58 |
| GHA | cr3 | 200 | 37205179.83 |
| GTM | baseline | 200 | 20658979.40 |
| GTM | null | 200 | 20658484.23 |
| GTM | cr1 | 200 | 20664270.61 |
| GTM | cr3 | 200 | 20662601.20 |
| GIN | baseline | 200 | 15268244.22 |
| GIN | null | 200 | 15267630.06 |
| GIN | cr1 | 200 | 15274806.92 |
| GIN | cr3 | 200 | 15272736.35 |
| GNB | baseline | 200 | 2333250.29 |
| GNB | null | 200 | 2333165.03 |
| GNB | cr1 | 200 | 2334161.31 |
| GNB | cr3 | 200 | 2333873.87 |
| HTI | baseline | 200 | 12689150.54 |
| HTI | null | 200 | 12688263.81 |
| HTI | cr1 | 200 | 12698625.88 |
| HTI | cr3 | 200 | 12695636.36 |
| IND | baseline | 200 | 1602828928.27 |
| IND | null | 200 | 1602777786.37 |
| IND | cr1 | 200 | 1603375415.22 |
| IND | cr3 | 200 | 1603202995.47 |
| IDN | baseline | 200 | 314764487.18 |
| IDN | null | 200 | 314753829.68 |
| IDN | cr1 | 200 | 314878369.97 |
| IDN | cr3 | 200 | 314842439.30 |
| IRN | baseline | 200 | 100227010.37 |
| IRN | null | 200 | 100223594.49 |
| IRN | cr1 | 200 | 100263511.47 |
| IRN | cr3 | 200 | 100251995.17 |
| IRQ | baseline | 200 | 50074605.42 |
| IRQ | null | 200 | 50072971.53 |
| IRQ | cr1 | 200 | 50092064.71 |
| IRQ | cr3 | 200 | 50086556.21 |
| JOR | baseline | 200 | 12722232.99 |
| JOR | null | 200 | 12721743.36 |
| JOR | cr1 | 200 | 12727465.11 |
| JOR | cr3 | 200 | 12725814.34 |
| KAZ | baseline | 200 | 22295533.44 |
| KAZ | null | 200 | 22295183.29 |
| KAZ | cr1 | 200 | 22299275.13 |
| KAZ | cr3 | 200 | 22298094.61 |
| KEN | baseline | 200 | 60295769.37 |
| KEN | null | 200 | 60293789.92 |
| KEN | cr1 | 200 | 60316921.17 |
| KEN | cr3 | 200 | 60310247.65 |
| MDG | baseline | 200 | 32020544.06 |
| MDG | null | 200 | 32018132.84 |
| MDG | cr1 | 200 | 32046309.61 |
| MDG | cr3 | 200 | 32038180.43 |
| MWI | baseline | 200 | 22466909.56 |
| MWI | null | 200 | 22465921.24 |
| MWI | cr1 | 200 | 22477470.47 |
| MWI | cr3 | 200 | 22474138.44 |
| MYS | baseline | 200 | 38594116.22 |
| MYS | null | 200 | 38593189.80 |
| MYS | cr1 | 200 | 38604015.63 |
| MYS | cr3 | 200 | 38600892.31 |
| MLI | baseline | 200 | 24867467.12 |
| MLI | null | 200 | 24866826.69 |
| MLI | cr1 | 200 | 24874310.57 |
| MLI | cr3 | 200 | 24872151.42 |
| MEX | baseline | 200 | 147926773.70 |
| MEX | null | 200 | 147923558.08 |
| MEX | cr1 | 200 | 147961134.80 |
| MEX | cr3 | 200 | 147950293.67 |
| MAR | baseline | 200 | 42373038.83 |
| MAR | null | 200 | 42371738.84 |
| MAR | cr1 | 200 | 42386930.15 |
| MAR | cr3 | 200 | 42382547.36 |
| MOZ | baseline | 200 | 36021943.28 |
| MOZ | null | 200 | 36020112.58 |
| MOZ | cr1 | 200 | 36041505.60 |
| MOZ | cr3 | 200 | 36035333.57 |
| MMR | baseline | 200 | 62440143.27 |
| MMR | null | 200 | 62438856.84 |
| MMR | cr1 | 200 | 62453889.74 |
| MMR | cr3 | 200 | 62449552.65 |
| NPL | baseline | 200 | 34271950.45 |
| NPL | null | 200 | 34271548.87 |
| NPL | cr1 | 200 | 34276241.67 |
| NPL | cr3 | 200 | 34274887.76 |
| NER | baseline | 200 | 28423766.51 |
| NER | null | 200 | 28422846.22 |
| NER | cr1 | 200 | 28433600.53 |
| NER | cr3 | 200 | 28430497.84 |
| NGA | baseline | 200 | 240643780.99 |
| NGA | null | 200 | 240633414.20 |
| NGA | cr1 | 200 | 240754557.28 |
| NGA | cr3 | 200 | 240719606.73 |
| PAK | baseline | 200 | 267437328.40 |
| PAK | null | 200 | 267433013.02 |
| PAK | cr1 | 200 | 267483441.16 |
| PAK | cr3 | 200 | 267468892.32 |
| PER | baseline | 200 | 43281751.18 |
| PER | null | 200 | 43281102.00 |
| PER | cr1 | 200 | 43288688.13 |
| PER | cr3 | 200 | 43286499.48 |
| PHL | baseline | 200 | 130197055.97 |
| PHL | null | 200 | 130191716.29 |
| PHL | cr1 | 200 | 130254114.15 |
| PHL | cr3 | 200 | 130236111.97 |
| RUS | baseline | 200 | 166446924.26 |
| RUS | null | 200 | 166443248.73 |
| RUS | cr1 | 200 | 166486199.82 |
| RUS | cr3 | 200 | 166473808.16 |
| RWA | baseline | 200 | 14783244.36 |
| RWA | null | 200 | 14781854.04 |
| RWA | cr1 | 200 | 14798100.92 |
| RWA | cr3 | 200 | 14793413.59 |
| SLE | baseline | 200 | 9523824.60 |
| SLE | null | 200 | 9523503.62 |
| SLE | cr1 | 200 | 9527254.55 |
| SLE | cr3 | 200 | 9526172.38 |
| ZAF | baseline | 200 | 66698388.90 |
| ZAF | null | 200 | 66695162.22 |
| ZAF | cr1 | 200 | 66732868.23 |
| ZAF | cr3 | 200 | 66721989.80 |
| LKA | baseline | 200 | 24902994.15 |
| LKA | null | 200 | 24901885.41 |
| LKA | cr1 | 200 | 24914841.76 |
| LKA | cr3 | 200 | 24911103.78 |
| SDN | baseline | 200 | 51272487.95 |
| SDN | null | 200 | 51270018.21 |
| SDN | cr1 | 200 | 51298878.86 |
| SDN | cr3 | 200 | 51290552.38 |
| TJK | baseline | 200 | 11386252.39 |
| TJK | null | 200 | 11386042.26 |
| TJK | cr1 | 200 | 11388497.79 |
| TJK | cr3 | 200 | 11387789.35 |
| TZA | baseline | 200 | 70421136.11 |
| TZA | null | 200 | 70416189.29 |
| TZA | cr1 | 200 | 70473996.35 |
| TZA | cr3 | 200 | 70457318.64 |
| THA | baseline | 200 | 80835063.32 |
| THA | null | 200 | 80832023.97 |
| THA | cr1 | 200 | 80867540.93 |
| THA | cr3 | 200 | 80857294.05 |
| TGO | baseline | 200 | 9720792.99 |
| TGO | null | 200 | 9720378.66 |
| TGO | cr1 | 200 | 9725220.35 |
| TGO | cr3 | 200 | 9723823.49 |
| TUR | baseline | 200 | 95533008.34 |
| TUR | null | 200 | 95527406.77 |
| TUR | cr1 | 200 | 95592865.06 |
| TUR | cr3 | 200 | 95573979.92 |
| UGA | baseline | 200 | 51327486.10 |
| UGA | null | 200 | 51324580.17 |
| UGA | cr1 | 200 | 51358537.94 |
| UGA | cr3 | 200 | 51348740.91 |
| UKR | baseline | 200 | 49788460.96 |
| UKR | null | 200 | 49787153.75 |
| UKR | cr1 | 200 | 49802429.44 |
| UKR | cr3 | 200 | 49798022.31 |
| UZB | baseline | 200 | 39408408.38 |
| UZB | null | 200 | 39407291.71 |
| UZB | cr1 | 200 | 39420340.73 |
| UZB | cr3 | 200 | 39416576.00 |
| VNM | baseline | 200 | 111504825.37 |
| VNM | null | 200 | 111501148.50 |
| VNM | cr1 | 200 | 111544115.26 |
| VNM | cr3 | 200 | 111531719.08 |
