# The Asthma Model, and its Scenarios
This document describes the Asthma state-transition model, and the scenarios which are run using it.
If you are uncertain about the general appendix 3 methodologies, or have general queries, [please refer to the README](README.md).

## Link to Model
- Baseline (as reference): [Link to Botech Online Model](https://botech.forecasthealth.org/?userId=appendix_3&modelId=asthma_baseline)


##  The Asthma Model and its design
### Asthma Models creates three scenarios: Null_Asthma, CR1, and CR3
The Asthma Model refers to a "Model architecture": A structure of states and transitions, which can be used to run different scenarios.
A scenario is when the structure has a different set of transition rates between the states.

The Asthma model is used to run two scenarios of treatment coverage: CR1 and CR3.
In addition, the Asthma model is also used to run a "Null Scenario": Called Asthma_Null.
We will explain the Null Scenario later.

### Structure of the Asthma Model
Asthma has three key states, `DsFreeSus`,  `AsthmaEpsd`, and `Deceased`.
`DsFreeSus` means "Disease free, susceptible", and this refers to the majority of the population.
`AsthmaEpsd` means "Asthma Episode", and generally refers to people who have asthma and will experience an episode that year.
`Deceased` refers to the people in the model who have died, either through background mortality (`DsFreeSus -> Deceased`) or through the Asthma episode (`AsthmaEpsd -> Deceased`).

In addition to these states, there are other "states" which are used to perform calculations, or collect useful statistics about the model.
This is something we have chosen to do in our model structure, so it's visible to users, but it is not strictly necessary.
For example, we have states for `Disability`, which collects information about the stock of `DsFreeSus`, `AsthmaEpsd` and `Deceased` and multiplies them against some disability weight.
We also have states to calculate births, migration, and the effects of interventions on disability and mortality.
Once again, we made these design decisions so that users can see how these work, but they aren't strictly necessary.
They can be done elsewhere, and simply rendered as a transition rate.

### The modelled treatments for Asthma
For Asthma, there are four treatments.
An intervention is something that has an effect on the main components of the model, such as disability, or mortality.
- LowDoseBeclom
    - Name in Spectrum: Low dose inhaled beclometasone + SABA
- HighDoseBeclom
    - Name in Spectrum: High dose inhaled beclometasone + SABA
- InhaledShortActingBeta
    - Name in Spectrum: Inhaled short acting beta agonist for intermittent asthma
- AsthmaOralPrednisolone
    - Name in Spectrum: Oral prednisolone + inhaled salbutamol and ipratroprium
 
While treatments are always present in the structure of the Asthma model, their coverage differs depending on the scenario.

### Treatment Impacts
**NOTE** - These figures imply a modification of effect sizes.
E.g. `LowDoseBeclom` reduces the CFR of `AsthmaEpsd` by 50% (-0.5).

- LowDoseBeclom
    - Disability: -0.07979948
    - Mortality: -0.5
- HighDoseBeclom
    - Disability:-0.13260075
- InhaledShortActingBeta
    - Disability:-0.00961066
- AsthmaOralPrednisolone
    - Disability:-0.3373407

### Population in Need
**NOTE** - Refers to the proportion of people in `AsthmaEpsd` who are "in need" of this treatment.
e.g. 30% of `AsthmaEpsd` are "in need" of `InhaledShortActingBeta`
- LowDoseBeclom: 0.4
- HighDoseBeclom: 0.3
- InhaledShortActingBeta: 0.3
- AsthmaOralPrednisolone: 0.323

### The Model has two key components
The Asthma model is large, but can be broken down into two components.
![Both Components Together](./static/asthma_both_components.png)

#### The main component moves people between states
![The Main Component](./static/asthma_main_component.png)

The main component has the states we've introduced: `DsFreeSus`, `AsthmaEpsd`, `Deceased`, `Disability`, `Births`.
Importantly there are some other states which sit between states:
- `DsFreeSus Disability` sits between `DsFreeSus` and `Disability`
- `AsthmaEpsd Disability` sits between `AsthmaEpsd` and `Disability`
- `AsthmaEpsd Mortality` sits between `AsthmaEpsd` and `Deceased`

These states aren't really states in a true sense. 
Rather, these states set the value of the transition rates around them.
So, for example, `DsFreeSus Disability` is really the transition rate for `DsFreeSus -> Disability`.
In the nomenclature of the Botech protocol, we call this a "Surrogate node".
This is a structural decision we have made, but it doesn't change the results.
Rather, we do this, so we can show how the calculations work to determine the disability and mortality effects.

#### The calculation component sets the transition rates
![The Calculation Component](./static/asthma_calculation_component.png)
The "Surrogate Nodes" mentioned above, are set by a series of calculations in the model.
We will explain these in detail below in the section "The Order of Operations".

### The Asthma model scenarios
#### The Asthma_Null scenario
In the Asthma_Null, the coverage of all treatments is set to its baseline in the first year of the projection, then 0% afterwards.

#### Scenario CR1 - Acute treatment of asthma exacerbations with inhaled bronchodilators and oral steroids
In CR1:
- LowDoseBeclom continues at its baseline coverage for the entirety of the run
- HighDoseBeclom continues at its baseline coverage for the entirety of the run
- InhaledShortActingBeta continues at its baseline coverage for the entirety of the run
- AsthmaOralPrednisolone is set at its baseline coverage for the first year (2019) of the projection, and then to 95% coverage for the rest of the projection.

#### Scenario CR3 - Long-term management of asthma with inhaled bronchodilator and low-dose beclometasone
In CR3:
- LowDoseBeclom is set at its baseline coverage for the first year (2019) of the projection, and then to 95% coverage for the rest of the projection.
- HighDoseBeclom is set at its baseline coverage for the first year (2019) of the projection, and then to 95% coverage for the rest of the projection.
- InhaledShortActingBeta is set at its baseline coverage for the first year (2019) of the projection, and then to 95% coverage for the rest of the projection.
- AsthmaOralPrednisolone continues at its baseline coverage for the entirety of the run

## The Asthma Model and its key assumptions
**NOTE** - A document is a difficult place to put entire lists of assumptions, as many of the assumptions we have change over time, and many of the assumptions are arrays of values, which apply to males and females differently, as well as different ages.

Therefore, please look at `./data/asthma.csv` as a reference guide for some assumptions.
Values for disability weights have come from `./data/Asthma.xlsx` which is taken from Spectrum.
Furthermore, even though measures of incidence, prevalence, and mortality may appear in this document, the final values were taken from `./data/GBD_Country_DATA.xlsx`.

### The baseline scenario is the default scenario
The baseline scenario has a coverage rate that is static, and continues from the start year to the end year.
This is important, because it *completely removes the effect of the Calculation Component*. 
This is because, in essence, the effect of treatments is governed by the calculation: `effect = impact * coverage * population in need`.
However, coverage is no the current coverage, but the difference between the current coverage, and the starting coverage.
Therefore: `effect = impact * (current_coverage - starting_coverage) * population in need`.
Because `current_coverage - starting_coverage = 0`, there is no effect to add to the default values for disability and mortality.

### The null scenario reduces the coverage, and therefore the impacts
In the null scenario, all treatments are reduced from the baseline coverage to zero.
For example, in Afghanistan, it is assumed that the baseline coverage rate is 5%.
Therefore: `effect = impact * (0 - 0.05) * population in need = impact * -0.05 * population in need`.
Therefore, in this country, the null scenario implies a 5% reduction in the impact of the four treatments.

### The scale-up scenario increases the coverage, and therefor the impacts
In the scale-up scenario, select treatments (one treatment in CR1, three treatments in CR3) are increased from baseline to 95% for the projection, starting in the second year.
For the treatments that aren't selected, they are left at the baseline level, and thus do not contribute to effect calculations.
Therefore, for a select treatment in Afghanistan: `effect = impact * (0.95 - 0.05) * population in need = impact * 0.9 * population in need`.

# What is the order of operations?
## What do we mean by the order of operations?
When you "run a model" you are telling the model to, for example:
- Put some values in `DsFreeSus` e.g. the population of Australia
- Move some of those values to `AsthmaEpsd` e.g. the incidence of Asthma
- Move some values from `AsthmaEpsd -> DsFreeSus` e.g. the remission rate of Asthma

However, the ordering of these can be important.
Therefore, the order of operations describes the order in which steps are taken each year the model runs.

## The order of operations
It may look complicated at first, but we can simplify it by working through one example.
We will use the example of `LowDoseBeclom` to show this affects disability and mortality.
Importantly, for all these calculations, do not imagine these are people being transferred between states.
Rather, imagine this is an alternative to using Microsoft Excel, for calculating some values that will become a transition rate.

### 1. Generate the population of the country in 2019
We do this using the UNDP World Population Prospects Data, for country, year.
The data that is returned is the number of people for sex, age (through 100).
Reference: https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2022_Population1JanuaryBySingleAgeSex_Medium_1950-2021.zip
Reference: https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2022_Population1JanuaryBySingleAgeSex_Medium_2022-2100.zip

### 2. Generate values for constants in the Calculation Component
We need to load the constants which are used to calculate the effects on disability and mortality. 
This is the second step of the model. 

### 3. Calculate the Coverage Rate
The coverage rate is calculated by `Coverage - Starting Coverage`.
For example, `LowDoseBeclom_Coverage - LowDoseBeclom_StartingCoverage`.
The result of this calculation is stored in, e.g. `LowDoseBeclom_Calculated_Coverage`

### 4. Calculate Disability Effects
Disability effects are calculated by: `PIN * Disability Impact * Coverage`
Therefore, using `LowDoseBeclom` as an example, we multiply `LowDoseBeclom_PIN`, `LowDoseBeclom_Disability_Impact` and `LowDoseBeclom_Calculated_Coverage`
We store this value in `LowDoseBeclom_Disability_Effect`.

### 5. Transform the Disability Effects
Here, we transform a value to its inverse by subtractring it from one. 
E.g. 1 - 0.05 = 0.95.
We do this for `LowDoseBeclom_Disability_Effect`, `HighDoseBeclom_Disability_Effect`, `AsthmaOralPrednisolone_Disability_Effect` and `InhaledShortActingBeta_Disability_Effect`. 
Therefore, the sequence might be: 1 - 0.05 - 0.03 - 0.02 - 0.00 = 0.90
We store this value in `Disability_Effect_Transform`. 

### 6. We calculate the "Blended Disability" for `AsthmaEpsd`
The default disability weight for `AsthmaEpsd` is not a static value.
Instead, it is determined by the following equation: `dw = 1 - ((1 - healthy_disability) * (1 - asthmaepsd_disability))`
We call this a "blended disability".

We calculate this in our model through the following:
- The constant loaded in `Asthma_Disability` is subtracted from 1
- The constant loaded in `Healthy_Disability` is subtracted from 1
- This value is stored in `Asthma_Blended_Disability`
- `Asthma_Blended_Disability` is subtracted from 1, and stored in `Blended_Disability_Transform`

### 7. Calculate `AsthmaEpsd Disability` surrogate value
We now have two values:
1. The default `AsthmaEpsd` disability weight (stored in `Blended_Disability_Transform`)
2. Some modifier of that disability weight, based on treatment impact, population in need, and coverages, stored in `Disability_Effect_Transform`

Therefore, we do two operations in this step:
1. Move the value from `Blended_Disability_Transform` into `AsthmaEpsd Disability`
2. Multiply `Disability_Effect_Transform` against the value in `AsthmaEpsd Disability`

Once this is set in the surrogate, it is propagated to the edges surrounding it. 

### 8. Calculate `DsFreeSus Disability` Surrogate
The disability weight for `DsFreeSus` is simply just the `Healthy_Disability` value.
Therefore, we just move this value to the `DsFreeSus Disability` state

### 9. Repeat Steps 3 - 8 but for Mortality
To determine the value in `AsthmaEpsd Mortality`, we follow very similar steps as have been described for `AsthmaEpsd Disability`.

### 10. Record the number of births that will occur
For states `DsFreeSus` and `AsthmaEpsd` we multiply the number of fertile women, against their age specific fertility rates (UNDP Statistics), to calculate the number of births.
NOTE - These women don't given birth yet, but we calculate births now, before people move states or die, or age or migrate.
Reference: https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2022_Fertility_by_Age1.zip

### 11 - Exchange between DsFreeSus and AsthmaEpsd
`DsFree -> AsthmaEpsd` and `AsthmaEpsd -> DsFree` are transacted (the incidence of asthma and remission of asthma respectively).

### 12 - Disability is Recorded
`DsFree -> Disability`, `AsthmaEpsd -> Disability` and `Deceased -> Disability` are recorded.
Using `AsthmaEpsd` as an example, let's explain this.
First, the stock of persons in `AsthmaEpsd` is counted e.g. 3,000.
Then, this stock is multiplied against the disability weight calculated and stored in `AsthmaEpsd Disability` e.g. 0.1
Then, disability is calculated as `3000 * 0.1 = 300`.
This value is sent and stored into `Disability`.

The disability weight for `AsthmaEpsd` is taken from Spectrum by Avenir Health.
The disability weight for `DsFreeSus` is taken from Spectrum by Avenir Health but is originally from GBD we believe.

### 13 - Populations migrate
Migration rates calculated using the UNDP World Population Projections are used to increase or decrease the current populations of people in `DsFreeSus` and `AsthmaEpsd`.
Reference: https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/EXCEL_FILES/1_General/WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx

### 14 - People get older
People get older by 1 year. 
If a person was 100, they are removed from the model at this point.

### 15 - People die
People move to the `Deceased` state via: `DsFreeSus -> Deceased`, `AsthmaEpsd -> Deceased`
The background mortality rate for `DsFreeSus -> Deceased` is taken from the UNDP World Population Projections lifetables (we use the rate "qx").

Reference: https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2022_Life_Table_Complete_Medium_Male_1950-2021.zip
Reference: https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2022_Life_Table_Complete_Medium_Male_2022-2100.zip

### 16 - Women give birth
The births that were stored in the `Births` state are transmitted to `DsFreeSus`.
The number of males and females are governed by the sex ratio from the UNDP World Population Projections database.

Reference: https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/EXCEL_FILES/1_General/WPP2022_GEN_F01_DEMOGRAPHIC_INDICATORS_COMPACT_REV1.xlsx

### 17 - Constants are cleared
Any constants or intermediate values that were calculated are cleared from the model, so they don't contribute to calculations in the next year.

### 18 - The timestep is incremented.
If the year was 2019, it is now 2020. 
If the year was 2020, it is now 2021.
If the year was 2119, the model simulation ends.

# Outstanding Issues / Clarifications / Questions
- Our current demographic projection may differ substantially from previous model's demographic project.
    - Changes to fertility rates, background mortality, and migration rates may all affect the magnitude of the results.
- We are not sure if there has been discounting on effects.

[Link to Results](https://forecasthealth.org/who-appendix3-cr/)
