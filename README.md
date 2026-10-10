---
title: Asthma epidemiology
module_identifier: ncd-asthma
owner: Forecast Health
last_updated: 2026-10-10
status: Executable source module
---

# Asthma epidemiology

## Contents

- [Purpose](#purpose)
- [Method](#method)
- [Inputs and outputs](#inputs-and-outputs)
- [Parameters and templates](#parameters-and-templates)
- [Data and evidence](#data-and-evidence)
- [Relationships](#relationships)
- [Assumptions and limitations](#assumptions-and-limitations)
- [Status](#status)

## Purpose

This module models asthma incidence, prevalence, disability and asthma deaths within the canonical demographic population, the single population by sex and single year of age that every disease module shares. It answers how many people live with asthma, how much disability and how many deaths asthma causes each year, and how those change when a clinical intervention or a risk-factor policy is applied.

## Method

Asthma is a marginal disease process: the module tracks only the asthma partition of the canonical population, not a separate population of its own. It has two living states. `AsthmaEpsd` holds people currently in an asthma episode, which here means people with active asthma. `DsFreeSus` (disease-free, susceptible) is everyone else. At each model-year opening the coordinator sets `DsFreeSus` to the canonical population minus `AsthmaEpsd`, by age and sex, so the two states always add up to the canonical population.

Three rates move people each year:

| Rate | From | To | Default source |
|---|---|---|---|
| Incidence | `DsFreeSus` | `AsthmaEpsd` | GBD asthma incidence from the data service (`fhdb` epidemiology, measure `incidence`), cases per person per year |
| Remission | `AsthmaEpsd` | `DsFreeSus` | Spectrum/OneHealth asthma remission (data service observation `AsthmaEpsd -> DsFreeSus`), fitted by age band (see Calibration) |
| Asthma fatality | `AsthmaEpsd` | death | GBD-based asthma death input from the data service (`fhdb` epidemiology, measure `deaths`), fitted to WHO deaths (see Calibration) |

GBD (the Global Burden of Disease study of the Institute for Health Metrics and Evaluation, IHME) counts every new asthma episode as incident, including a relapse after remission. The model keeps that definition: a person who remits returns to `DsFreeSus` and can have asthma again through incidence.

The three rates are applied together as competing continuous hazards on the balance at the start of the phase, so their order in the file does not change the result. Background mortality, the demographic module's other-cause death rate, is then applied to the balance left in `AsthmaEpsd`. At the annual rebase, other-cause deaths are the demographic all-cause deaths less the modelled asthma deaths, and they are removed from each state in proportion to its size. People with asthma therefore die of other causes at the same rate as people without asthma. The shared survivor relative-mortality fit, which gives people with stroke, ischaemic heart disease, diabetes or chronic obstructive pulmonary disease (COPD) a fitted multiple of the other-cause death rate, is not declared for asthma; asthma prevalence is held by the remission fit instead.

### Intervention and risk-factor effects

A risk-factor module can multiply asthma incidence. Tobacco is the one that does: `risk-factor-tobacco` supplies the ratio of the comparison's to the baseline's population mean smoking-related asthma risk, which multiplies incidence before the incidence transition. Breastfeeding promotion adds no asthma route; the `risk-factor-breastfeeding` README gives the evidence.

Clinical interventions act through two shared landing nodes that this module owns:

- `Disability_Effect_Transform`. Each selected intervention adds its disability effect, and the asthma disability weight in that year is 0.039 × (1 − the sum of the effects).
- `Mortality_Effect_Transform`. Each selected intervention adds its mortality effect, and the asthma fatality rate in that year is multiplied by (1 − the sum of the effects).

Each intervention's effect is its population-in-need share × (coverage in that year − baseline coverage) × its impact. Treatment already given at baseline coverage therefore has no modelled effect; the observed rates the module is calibrated to already include it. In the baseline scenario coverage stays at the baseline value, so every effect is zero.

### Calibration

The [opening-state contract](data/asthma-opening-state.contract.v3.json) declares a rate calibration that the shared `opening-state-reconciliation` module applies once before the first model year. The fit uses the baseline template's inputs, and the same result is used for the baseline and every comparison, so a user's scenario edits do not change it.

1. Asthma deaths. The asthma fatality input is scaled by sex and single year of age so the opening year's asthma deaths equal the WHO Global Health Estimates 2021 (GHE) asthma death rate applied to the opening population. GHE reports deaths in seven age bands (0–4, 5–14, 15–29, 30–49, 50–59, 60–69, and 70 years and over). Within each band the deaths are spread across single ages in proportion to the GBD asthma death rate (the GBD deaths input times GBD prevalence). WHO GHE 2021 is the death target because it is WHO's own estimate and is consistent across countries; GBD supplies the age shape within bands, incidence and prevalence.
2. Remission. Remission is scaled in 12 age bands (0–4, 5–9, 10–14, 15–19, 20–24, 25–29, 30–39, 40–49, 50–59, 60–69, 70–79, and 80 years and over), to between 0.5 and 10 times the Spectrum value, so that one model year carries observed age-specific prevalence forward unchanged. Remission is the rate the source data identify least well, so it is the one fitted. Incidence keeps the GBD value.

Before the remission fit, the Spectrum remission was too low for GBD incidence and prevalence: in Indonesia, age-standardised asthma prevalence rose 77% from 2025 to 2050 without any intervention. With the fit the change is −4%. The same calibration lowered Indonesia's 2025 asthma deaths from 33,922 to 27,149. These figures come from the Indonesia check run when the calibration was released and recorded in the NCD client changelog.

### Disability weights

A model state that holds one GBD health state takes that state's weight. A state that combines several GBD sequelae takes the GBD 2019 global average for those sequelae, which is the cause's years lived with disability divided by its prevalent cases. That average weights each severity level by GBD's own severity distribution, which GBD models by location and does not publish as a table. A person with two modelled conditions takes GBD's multiplicative combination, 1 − (1 − w1)(1 − w2).

| Model state | Old | GBD weight | GBD health states and mapping |
|---|---|---|---|
| Asthma episode (`AsthmaEpsd`, node `Asthma_Disability`) | 0.016–0.098 by region | 0.039 | Asthma: asymptomatic 0, controlled 0.015, partially controlled 0.036, uncontrolled 0.133. GBD 2019 global average: 10.20 million YLDs over 262.4 million cases. GBD's US MEPS severity split (36.2% asymptomatic, 19.9% controlled, 20.6% partially controlled, 23.3% uncontrolled) gives 0.041. |

Until October 2026 the weight was read from the data service observation `AsthmaEpsd -> Disability`, a Spectrum/OneHealth value by region and age (0.016 to 0.098) without a cited source. Sources: GBD 2019 Diseases and Injuries Collaborators, *Lancet* 2020;396:1204–22, appendix 1 (the disability-weight table in each cause section) and appendix 2, table S18 (global prevalence and years lived with disability, 2019); the IHME GBD 2019 disability-weights table; Salomon JA et al., *Lancet Glob Health* 2015;3:e712–23, where the weights were estimated.

## Inputs and outputs

All arrays are 2 × 101: two sexes by single years of age 0 to 100.

| Input | Meaning | Units | Required |
|---|---|---|---|
| Opening population | Canonical population from the demographic module | people | yes |
| Opening asthma prevalence | GBD asthma prevalence, allocated to `AsthmaEpsd` by `opening-state-reconciliation` | proportion | yes |
| Background mortality rate | Demographic other-cause death rate | annual rate | yes |
| Net migration rate | Demographic net migration, applied in proportion to both living states | annual rate | no |
| Incidence modifier | Risk-factor multiplier on asthma incidence | multiplier | no |
| Disability and mortality effects | Clinical intervention effects, added into the two transforms | proportion | no |

| Output | Meaning | Units |
|---|---|---|
| `asthma_episode_population` | People in `AsthmaEpsd` | people |
| `asthma_incidence_flow` | New asthma episodes in the year | people |
| `asthma_mortality_flow` | Asthma deaths in the year, excluding other-cause deaths | people |

The module also records the asthma disability weight for each year. The `metric-health-burden` module calculates years lived with disability (YLD), years of life lost (YLL) and disability-adjusted life years (DALYs) from these rows, as declared in the [metric-input contract](interface/asthma-epidemiology-core.metric-inputs.v1.json). The disease graph itself contains no YLD, YLL or DALY calculation.

## Parameters and templates

The module has one template, `asthma_baseline`, which sets no overrides. The [parameter registry](parameters/registry.v1.json) declares one parameter, `asthma_disability_weight` (default 0.039, range 0 to 1), which the module owns and a scenario cannot edit. All editable asthma scenario parameters belong to the intervention modules below.

The client offers two asthma intervention codes from Appendix 3 of the WHO best-buys list. The compiler assembles each from separate intervention repositories, which connect to this module's two transforms:

| Code | Compiled package | Title | Intervention modules |
|---|---|---|---|
| CR1 | `ncd-asthma-cr1` | Acute treatment of asthma exacerbations with inhaled bronchodilators and oral steroids | `ncd-asthma-asthmaoralprednisolone` (oral prednisolone) |
| CR3 | `ncd-asthma-cr3` | Long-term management of asthma with inhaled bronchodilator and low-dose beclometasone | `ncd-asthma-inhaledshortactingbeta` (inhaled short-acting beta agonist, SABA), `ncd-asthma-lowdosebeclom` (low-dose beclometasone plus SABA) and `ncd-asthma-highdosebeclom` (high-dose beclometasone plus SABA) |

Selecting CR3 brings in all three of its modules together, and each sets its own target coverage to 0.95 in the comparison. Only low-dose beclometasone reduces asthma fatality; the other three modules reduce disability only. Each module's README gives its effect size, population in need and baseline coverage.

## Data and evidence

[`model.json`](model.json) is the executable disease graph. The [module contract](interface/asthma-epidemiology-core.module.contract.v1.json) defines composition and runtime semantics. The [opening-state recipe](data/asthma-opening-balance-seed.recipe.v1.json) allocates observed prevalence to the opening states, and the [opening-state contract](data/asthma-opening-state.contract.v3.json) declares the calibration.

| Input | Source |
|---|---|
| Opening population | Data service population (`fhdb.population`) |
| Prevalence, incidence, death age pattern | GBD asthma estimates served by the data service (`fhdb` epidemiology), from the Spectrum/OneHealth NCD defaults |
| Remission before fitting | Spectrum/OneHealth asthma model, data service observation `AsthmaEpsd -> DsFreeSus` |
| Death target | WHO Global Health Estimates 2021, asthma (`who_ghe.cause_death_rate`) |
| Disability weight | GBD 2019 (table above) |
| Years of life lost by age | GBD reference life table (IHME), 2019 values |

Routine care is the treatment people with asthma already receive whether or not an intervention is selected. It is declared in [`resource_requirements.json`](resource_requirements.json) as `routine_care_services`. Each entry names a service by the module and block that declare it, `ncd-asthma-inhaledshortactingbeta` (`cr3-inhaled-short-acting-beta`), `ncd-asthma-lowdosebeclom` (`cr3-low-dose-beclometasone-saba`) and `ncd-asthma-highdosebeclom` (`cr3-high-dose-beclometasone-saba`), and delivers it to `AsthmaEpsd`. This module does not copy the services' resources. The compiler takes the quantities, cost items, population in need and baseline coverage from each service's own declaration and costs the service at its baseline coverage in both scenarios. When the owning intervention is selected, its block also costs the service for the population the intervention reaches, at baseline coverage in the baseline scenario and at the target coverage in the comparison. The CR1 acute-treatment service is declared only by `ncd-asthma-asthmaoralprednisolone` and is not routine care here.

Staff time is priced from one shared salary item per staff type, `cost-item.workforce-salary.<type>`. The asthma services use two types, `nurse` and `generalist-primary-care-doctor`, and a type is the same item in every module that uses it, so a nurse minute costs the same everywhere. The item is an annual salary. Its default is the country's WHO-CHOICE annual salary from the data service for the type's cadre (skill level 4 for doctors, 3 for nurses). A staff minute costs that salary divided by 126,720 working minutes a year (8 hours, 22 days a month, 12 months), the convention the data service uses for its WHO-CHOICE cost per minute. The per-minute values in the resource graphs are defaults for use without a country.

## Relationships

The demographic module supplies the canonical population, background mortality and migration. The annual coordinator derives the asthma population at risk from the canonical population and the current asthma state. `opening-state-reconciliation` creates one opening state and one calibration for both scenarios. `risk-factor-tobacco` can modify incidence. The four intervention repositories in the table above own the clinical intervention graph slices. `metric-health-burden` calculates YLD, YLL and DALYs from this module's outputs.

## Assumptions and limitations

- The disease-free state is a residual, not an additional population. The asthma estimate is marginal: it does not interact with other diseases a person may have.
- Asthma has one living disease state with one disability weight, the GBD global average across severity levels. Better control can only be represented as a proportional cut in that average weight, and the weight does not vary by country.
- People with asthma die of other causes at the same rate as people without asthma. If asthma carries excess non-asthma mortality, the model overstates the number of people living with asthma at older ages.
- The calibration fixes deaths and prevalence in the opening year only. Later years follow from the fitted rates and the demographic projection; incidence does not change over time except through a risk-factor modifier.
- Intervention effects from different modules are added. When CR1 and CR3 are both selected, their disability effects are summed in the same year, which assumes they do not overlap.
- Treatment at baseline coverage has no modelled effect, and routine care at baseline coverage is costed in both scenarios. Acute CR1 treatment at baseline coverage is costed only when CR1 is selected.

## Status

The disease graph, compiler contract, baseline template, opening-state recipe and rate calibration are implemented, and the contract validator passes. The source graph needs compiler lowering and is not a standalone national model. The module contract still lists economic helper nodes from the old all-in-one model as unresolved, although the current graph no longer contains them.
