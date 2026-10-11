---
title: Asthma epidemiology
module_identifier: ncd-asthma
owner: Forecast Health
last_updated: 2026-10-11
status: Executable source module
---

# Asthma epidemiology

## Contents

- [Purpose](#purpose)
- [Inputs and outputs](#inputs-and-outputs)
- [Method](#method)
- [Routine care costs](#routine-care-costs)
- [Parameters](#parameters)
- [Data and evidence](#data-and-evidence)
- [Validation](#validation)
- [Assumptions and limitations](#assumptions-and-limitations)
- [Relationships](#relationships)
- [Status](#status)

## Purpose

This module models asthma incidence, prevalence, disability and asthma deaths within the canonical demographic population. The canonical population is the single population, by sex and single year of age, that every disease module shares.

The module answers how many people live with asthma, how much disability and how many deaths asthma causes each year, and how those numbers change when a clinical intervention or a risk-factor policy is applied.

## Inputs and outputs

All arrays are 2 × 101: two sexes by single years of age 0 to 100.

| Input | Meaning | Units | Required |
|---|---|---|---|
| Opening population | Canonical population from the demographic module | people | yes |
| Opening asthma prevalence | Share of each age and sex with asthma, from the Global Burden of Disease (GBD) study of the Institute for Health Metrics and Evaluation (IHME), allocated to the asthma state by `opening-state-reconciliation` | proportion | yes |
| Background mortality rate | The demographic module's death rate from causes other than asthma | annual rate | yes |
| Net migration rate | Demographic net migration, applied in proportion to both living states | annual rate | no |
| Incidence modifier | A risk-factor module's multiplier on asthma incidence | multiplier | no |
| Disability and mortality effects | Proportional cuts from clinical interventions, added together | proportion | no |

| Output | Meaning | Units |
|---|---|---|
| `asthma_episode_population` | People with active asthma | people |
| `asthma_incidence_flow` | New asthma episodes in the year | people |
| `asthma_mortality_flow` | Asthma deaths in the year, excluding deaths from other causes | people |

The module also records the asthma disability weight for each year. The `metric-health-burden` module calculates years lived with disability (YLD), years of life lost (YLL) and disability-adjusted life years (DALYs) from these rows, as declared in the metric-input contract (`interface/asthma-epidemiology-core.metric-inputs.v1.json`). The disease graph itself contains no YLD, YLL or DALY calculation.

## Method

### States and rates

Asthma is a marginal disease process. The module tracks only the asthma partition of the canonical population, not a separate population of its own. It has two living states. `AsthmaEpsd` holds people currently in an asthma episode, which here means people with active asthma. `DsFreeSus` (disease-free, susceptible) holds everyone else. At the start of each model year the annual coordinator sets `DsFreeSus` to the canonical population minus `AsthmaEpsd`, by age and sex, so the two states always add up to the canonical population.

Spectrum/OneHealth is the OneHealth Tool, a costing and planning model in the Spectrum suite used by the World Health Organization (WHO) and other United Nations agencies, whose noncommunicable disease (NCD) defaults supply several inputs. Three rates move people each year:

| Rate | From | To | Default source |
|---|---|---|---|
| Incidence | `DsFreeSus` | `AsthmaEpsd` | GBD asthma incidence from the data service (`fhdb` epidemiology, measure `incidence`), cases per person per year |
| Remission | `AsthmaEpsd` | `DsFreeSus` | Spectrum/OneHealth asthma remission (data service observation `AsthmaEpsd -> DsFreeSus`), annual rate, scaled by age band before the first model year |
| Asthma fatality | `AsthmaEpsd` | death | GBD-based asthma death input from the data service (`fhdb` epidemiology, measure `deaths`), annual rate, scaled to WHO death estimates before the first model year |

GBD counts every new asthma episode as incident, including a relapse after remission. The model keeps that definition: a person who remits returns to `DsFreeSus` and can have asthma again through incidence.

The three rates are applied together as competing continuous hazards on each state's balance at the start of the phase, so their order in the file does not change the result. Background mortality is then applied to the balance left in `AsthmaEpsd`. At the annual rebase, other-cause deaths are the demographic all-cause deaths less the modelled asthma deaths, and they are removed from each state in proportion to its size. People with asthma therefore die of other causes at the same rate as people without asthma. Stroke, ischaemic heart disease, diabetes and chronic obstructive pulmonary disease (COPD) use a shared survivor relative-mortality fit, which gives people with the disease a fitted multiple of the other-cause death rate. Asthma does not declare that fit. Its prevalence is held by the remission fit instead.

### Calibration

The opening-state contract (`data/asthma-opening-state.contract.v3.json`) declares a rate calibration that the shared `opening-state-reconciliation` module applies once before the first model year. The fit uses the baseline template's inputs, and the same result is used for the baseline and every comparison, so a user's scenario edits do not change it. It has two steps.

1. Asthma deaths. The asthma fatality input is scaled by sex and single year of age so the opening year's asthma deaths equal the WHO Global Health Estimates 2021 (GHE) asthma death rate applied to the opening population. GHE reports deaths in seven age bands (0–4, 5–14, 15–29, 30–49, 50–59, 60–69, and 70 years and over). Within each band the deaths are spread across single ages in proportion to the GBD asthma death rate, the GBD deaths input times GBD prevalence. WHO GHE 2021 is the death target because it is WHO's own estimate and is consistent across countries. GBD supplies the age shape within bands, incidence and prevalence.
2. Remission. Remission is scaled in 12 age bands (0–4, 5–9, 10–14, 15–19, 20–24, 25–29, 30–39, 40–49, 50–59, 60–69, 70–79, and 80 years and over), to between 0.5 and 10 times the Spectrum/OneHealth value, so that one model year carries observed age-specific prevalence forward unchanged. Remission is the rate the source data identify least well, so it is the one fitted. Incidence keeps the GBD value.

### Disability weights

A disability weight is the GBD measure of health loss in a health state, on a scale from 0 (full health) to 1 (equivalent to death). A model state that holds one GBD health state takes that state's weight. A state that combines several GBD sequelae (the health states that follow from a cause) takes the GBD 2019 global average for those sequelae, which is the cause's YLD divided by its prevalent cases. That average weights each severity level by GBD's own severity distribution, which GBD models by location and does not publish as a table. A person with two modelled conditions with weights $w_1$ and $w_2$ takes GBD's multiplicative combination, $1 - (1 - w_1)(1 - w_2)$.

| Model state | GBD weight | GBD health states and mapping |
|---|---|---|
| Asthma episode (`AsthmaEpsd`, node `Asthma_Disability`) | 0.039 | Asthma: asymptomatic 0, controlled 0.015, partially controlled 0.036, uncontrolled 0.133. GBD 2019 global average: 10.20 million YLDs over 262.4 million cases. GBD's severity split from the US Medical Expenditure Panel Survey (MEPS) (36.2% asymptomatic, 19.9% controlled, 20.6% partially controlled, 23.3% uncontrolled) gives 0.041. |

The module does not use the Spectrum/OneHealth disability values for asthma (data service observation `AsthmaEpsd -> Disability`), which vary by region and age from 0.016 to 0.098 and have no cited source.

### Risk-factor and intervention effects

A risk-factor module can multiply asthma incidence. Tobacco is the one that does. `risk-factor-tobacco` supplies the ratio of the comparison's population mean smoking-related asthma risk to the baseline's, and incidence in year $t$ becomes $i_t = i\,m_t$, where $i$ is the GBD incidence rate (cases per person per year) and $m_t$ is that ratio. Breastfeeding promotion adds no asthma route. The `risk-factor-breastfeeding` README gives the evidence.

Clinical interventions act through two shared landing nodes that this module owns, `Disability_Effect_Transform` and `Mortality_Effect_Transform`. Each selected intervention $k$ adds its disability effect $E_{k,t}$ to the first and its mortality effect $M_{k,t}$ to the second. Each effect is

$$
E_{k,t} = p_k\,(c_{k,t} - c_{k,0})\,I_{D,k}, \qquad M_{k,t} = p_k\,(c_{k,t} - c_{k,0})\,I_{M,k}
$$

where $p_k$ is the intervention's population in need (the share of people with active asthma eligible for it), $c_{k,t}$ is its coverage in year $t$, $c_{k,0}$ is its baseline coverage (both shares of the population in need), and $I_{D,k}$ and $I_{M,k}$ are its disability and mortality impacts (proportional cuts per person newly treated). The asthma disability weight $w_t$ and the asthma fatality rate $f_t$ (deaths per person with active asthma per year) in year $t$ are then

$$
w_t = 0.039\,\Bigl(1 - \sum_k E_{k,t}\Bigr), \qquad f_t = f\,\Bigl(1 - \sum_k M_{k,t}\Bigr)
$$

where 0.039 is the GBD asthma disability weight, and $f$ is the calibrated asthma fatality rate. Treatment already given at baseline coverage has no modelled effect, because the observed rates the module is calibrated to already include it. In the baseline scenario coverage stays at the baseline value, so every effect is zero.

## Routine care costs

Routine care is the treatment people with asthma already receive whether or not an intervention is selected. It is declared in `resource_requirements.json` as `routine_care_services`. Each entry names a service by the module and block that declare it and delivers it to `AsthmaEpsd`. The three services are inhaled short-acting beta agonist (SABA) alone (`ncd-asthma-inhaledshortactingbeta`, block `cr3-inhaled-short-acting-beta`), low-dose beclometasone plus SABA (`ncd-asthma-lowdosebeclom`, block `cr3-low-dose-beclometasone-saba`) and high-dose beclometasone plus SABA (`ncd-asthma-highdosebeclom`, block `cr3-high-dose-beclometasone-saba`).

This module does not copy the services' resources. The compiler, the platform service that assembles selected modules into one runnable model, takes the quantities, cost items, population in need and baseline coverage from each service's own declaration. It costs the service at its baseline coverage in both scenarios. When the owning intervention is selected, its block costs the service for everyone the intervention reaches, at baseline coverage in the baseline scenario and at target coverage in the comparison, including the people routine care would treat. Each entry names `AsthmaEpsd` as the population `asthma_episode_population` (`population_channel_id`), the channel the CR3 components read, so when CR3 is selected the compiler leaves its three services out of routine care and each scenario counts those people once. The CR1 acute-treatment service is declared only by `ncd-asthma-asthmaoralprednisolone` and is not routine care here.

Staff time is priced from one shared salary item per staff type, `cost-item.workforce-salary.<type>`. The asthma services use two types, `nurse` and `generalist-primary-care-doctor`. A type is the same item in every module that uses it, so a nurse minute costs the same everywhere. The item is an annual salary. Its default is the country's annual salary from WHO-CHOICE (WHO CHOosing Interventions that are Cost-Effective), served by the data service for the type's cadre: skill level 4 for doctors and 3 for nurses. A staff minute costs that salary divided by 126,720 working minutes a year (8 hours a day, 22 days a month, 12 months), the convention the data service uses for its WHO-CHOICE cost per minute. The per-minute values in the resource graphs are defaults for use without a country.

## Parameters

The module has one template, `asthma_baseline`, which sets no overrides. The parameter registry (`parameters/registry.v1.json`) declares one parameter. The module owns it and a scenario cannot edit it.

| Parameter | Meaning | Baseline default | Comparison default | Range | Source |
|---|---|---|---|---|---|
| Asthma disability weight (`asthma_disability_weight`) | Disability weight of a person with active asthma before intervention effects | 0.039 | 0.039 | 0–1 | GBD 2019 |

All editable asthma scenario parameters belong to the intervention modules. The client offers two asthma intervention codes from Appendix 3 of the WHO best-buys list, WHO's list of recommended interventions for NCDs. The compiler assembles each from separate intervention repositories, which connect to this module's two transforms:

| Code | Compiled package | Title | Intervention modules |
|---|---|---|---|
| CR1 | `ncd-asthma-cr1` | Acute treatment of asthma exacerbations with inhaled bronchodilators and oral steroids | `ncd-asthma-asthmaoralprednisolone` (oral prednisolone) |
| CR3 | `ncd-asthma-cr3` | Long-term management of asthma with inhaled bronchodilator and low-dose beclometasone | `ncd-asthma-inhaledshortactingbeta` (SABA alone), `ncd-asthma-lowdosebeclom` (low-dose beclometasone plus SABA) and `ncd-asthma-highdosebeclom` (high-dose beclometasone plus SABA) |

Selecting CR3 brings in all three of its modules together, and each sets its own target coverage to 0.95 in the comparison. Only low-dose beclometasone reduces asthma fatality. The other three modules reduce disability only. Each module's README gives its effect size, population in need and baseline coverage.

## Data and evidence

`model.json` is the executable disease graph. The module contract (`interface/asthma-epidemiology-core.module.contract.v1.json`) defines composition and runtime semantics. The opening-state recipe (`data/asthma-opening-balance-seed.recipe.v1.json`) allocates observed prevalence to the opening states, and the opening-state contract (`data/asthma-opening-state.contract.v3.json`) declares the calibration.

| Input | Source |
|---|---|
| Opening population | Data service population (`fhdb.population`) |
| Prevalence, incidence, death age pattern | GBD asthma estimates served by the data service (`fhdb` epidemiology), from the Spectrum/OneHealth NCD defaults |
| Remission before fitting | Spectrum/OneHealth asthma model, data service observation `AsthmaEpsd -> DsFreeSus` |
| Death target | WHO Global Health Estimates 2021, asthma (`who_ghe.cause_death_rate`) |
| Disability weight | GBD 2019 |
| Years of life lost by age | GBD reference life table (IHME), 2019 values |

Disability-weight sources:

- GBD 2019 Diseases and Injuries Collaborators. Global burden of 369 diseases and injuries in 204 countries and territories, 1990–2019: a systematic analysis for the Global Burden of Disease Study 2019. *Lancet* 2020;396:1204–22. Appendix 1 gives the disability-weight table in each cause section. Appendix 2, table S18, gives global prevalence and years lived with disability for 2019.
- IHME. GBD 2019 disability weights table.
- Salomon JA, et al. Disability weights for the Global Burden of Disease 2013 study. *Lancet Glob Health* 2015;3:e712–23. The weights were estimated in this study.

## Validation

An Indonesia check, run when the calibration was released and recorded in the NCD client changelog, shows the effect of the two calibration steps. With the uncalibrated Spectrum/OneHealth remission, remission is too low for GBD incidence and prevalence: age-standardised asthma prevalence rises 77% from 2025 to 2050 without any intervention. With the remission fit the change is −4%. The death calibration gives 27,149 asthma deaths in Indonesia in 2025, against 33,922 from the uncalibrated input.

## Assumptions and limitations

- The disease-free state is a residual, not an additional population. The asthma estimate is marginal: it does not interact with other diseases a person may have.
- Asthma has one living disease state with one disability weight, the GBD global average across severity levels. Better control can only be represented as a proportional cut in that average weight, and the weight does not vary by country.
- People with asthma die of other causes at the same rate as people without asthma. If asthma carries excess non-asthma mortality, the model overstates the number of people living with asthma at older ages.
- The calibration fixes deaths and prevalence in the opening year only. Later years follow from the fitted rates and the demographic projection. Incidence does not change over time except through a risk-factor modifier.
- Intervention effects from different modules are added. When CR1 and CR3 are both selected, their disability effects are summed in the same year, which assumes they do not overlap.
- Treatment at baseline coverage has no modelled effect, and routine care at baseline coverage is costed in both scenarios. Acute CR1 treatment at baseline coverage is costed only when CR1 is selected.

## Relationships

The demographic module supplies the canonical population, background mortality and migration. The annual coordinator derives the asthma population at risk from the canonical population and the current asthma state. `opening-state-reconciliation` creates one opening state and one calibration for both scenarios. `risk-factor-tobacco` can modify incidence. The four intervention repositories listed under Parameters own the clinical intervention graph slices. `metric-health-burden` calculates YLD, YLL and DALYs from this module's outputs.

## Status

The disease graph, compiler contract, baseline template, opening-state recipe and rate calibration are implemented, and the contract validator passes. The source graph needs compiler lowering and is not a standalone national model. The module contract still lists economic helper nodes from the old all-in-one model as unresolved, although the current graph no longer contains them.
