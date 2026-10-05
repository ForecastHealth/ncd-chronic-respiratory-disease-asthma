---
title: Asthma epidemiology
module_identifier: ncd-asthma
owner: Forecast Health
last_updated: 2026-10-05
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

This module models asthma incidence, prevalence, disability, and cause-specific mortality within the canonical demographic population.

## Method

Asthma is a marginal disease process with two living states: an asthma episode state and a derived disease-free residual. At each model-year opening, the coordinator sets the residual to the canonical population minus the asthma episode population, by age and sex. During the year, incidence moves people from the residual to the asthma episode state. Disease transitions use a continuous-hazard competing-transition calculation based on the phase-opening balance. Background mortality then applies to the asthma episode state.

Clinical intervention components can reduce the asthma disability weight and case fatality through declared shared transforms. A risk-factor module can modify asthma incidence. The asthma graph publishes raw state and death results; metric modules calculate healthy years, years lived with disability, years of life lost, and disability-adjusted life years.

### Calibration

The [opening-state contract](data/asthma-opening-state.contract.v3.json) declares a rate calibration that the shared `opening-state-reconciliation` preflight applies before the first model year, with one result for baseline and every comparison. The asthma fatality input is scaled by sex and single age so the opening year's asthma deaths equal WHO Global Health Estimates 2021 asthma death rates applied to the opening population, distributed within each GHE age band by the GBD age pattern. Remission is scaled by GBD age band, within 0.5 to 10 times the Spectrum value, so the year carries observed age-specific prevalence forward unchanged. The Spectrum remission was two to nine times lower than GBD incidence and prevalence imply, and prevalence nearly doubled by 2050 without intervention. GBD incidence counts new episodes, so remitted people can have asthma again.

## Inputs and outputs

Required inputs are the canonical opening population, reconciled asthma opening prevalence and background mortality rates. Optional inputs are net migration rates, an incidence modifier, clinical disability effects and clinical mortality effects. The module publishes the asthma episode population, asthma incidence flow and asthma-specific mortality flow as age-sex arrays.

## Parameters and templates

The source module exposes only `asthma_baseline`. The parameter registry declares the asthma disability weight below as a module-owned parameter that is not editable in a scenario; it places its value on node `Asthma_Disability` in `model.json`. Comparison values belong to selected intervention modules. The compiler assembles Appendix 3 CR1 and CR3 from their separate intervention repositories.

## Data and evidence

[`model.json`](model.json) is the executable disease graph. The [module contract](interface/asthma-epidemiology-core.module.contract.v1.json) defines composition and runtime semantics. The [opening-state recipe](data/asthma-opening-balance-seed.recipe.v1.json) defines baseline initialization. The contract identifies Spectrum/OneHealth asthma material and the current method-fix reference as default provenance.

Routine care is declared in [`resource_requirements.json`](resource_requirements.json) as `routine_care_services`: each entry names a service by the module and block that declare it, `ncd-asthma-inhaledshortactingbeta` (`cr3-inhaled-short-acting-beta`), `ncd-asthma-lowdosebeclom` (`cr3-low-dose-beclometasone-saba`) and `ncd-asthma-highdosebeclom` (`cr3-high-dose-beclometasone-saba`), with the disease states it is delivered to. This module does not copy the services' resources. The compiler takes the quantities, cost items, population in need and baseline coverage from each service's own declaration and costs the service at its baseline coverage in both scenarios. When the owning intervention is selected, its block also costs the service for the population the intervention reaches, at baseline coverage in the baseline scenario and at the target coverage in the comparison; routine care of the disease states continues beside it from the same declaration. The CR1 acute-treatment service is declared only by `ncd-asthma-asthmaoralprednisolone`; this module's former copy of it was not costed and has been removed.

Staff time is priced from one shared salary item per staff type, `cost-item.workforce-salary.<type>`: `nurse`, `generalist-primary-care-doctor`, `specialist`, `therapist` and `counsellor`. A type is the same item in every module that uses it, so a generalist minute costs the same everywhere, and each type can be edited on its own: a specialist can be paid differently from a generalist doctor. The item is an annual salary. Its default is the country's WHO-CHOICE annual salary from the data service for the type's cadre (skill level 4 for doctors and specialists, 3 for nurses and therapists, 2 for counsellors); the cadre is the default source, not the item. A staff minute costs that salary divided by 126,720 working minutes a year (8 hours, 22 days a month, 12 months). The data service uses this convention for its WHO-CHOICE cost per minute, and every clinical staff cost has used it. The per-minute values in the resource graphs are defaults for use without a country. Tobacco policy programme roles are separate staff types, since none is the same job as a clinical one.

### Disability weights

A model state that holds one GBD health state takes that state's weight. A state that combines several GBD sequelae takes the GBD 2019 global average for those sequelae, which is the cause's years lived with disability divided by its prevalent cases. That average weights each severity level by GBD's own severity distribution, which GBD models by location and does not publish as a table. A person with two modelled conditions takes GBD's multiplicative combination, 1 − (1 − w1)(1 − w2).

| Model state | Old | GBD weight | GBD health states and mapping |
|---|---|---|---|
| Asthma episode (`AsthmaEpsd`, node `Asthma_Disability`) | 0.016–0.098 by region | 0.039 | Asthma: asymptomatic 0, controlled 0.015, partially controlled 0.036, uncontrolled 0.133. GBD 2019 global average: 10.20 million YLDs over 262.4 million cases. GBD's US MEPS severity split (36.2% asymptomatic, 19.9% controlled, 20.6% partially controlled, 23.3% uncontrolled) gives 0.041. |

Until October 2026 the weight was read from the data service observation `AsthmaEpsd -> Disability`, a Spectrum/OneHealth value by region and age (0.016 to 0.098) without a cited source. Clinical interventions still reduce the weight through `Disability_Effect_Transform`. Sources: GBD 2019 Diseases and Injuries Collaborators, *Lancet* 2020;396:1204–22, appendix 1 (the disability-weight table in each cause section) and appendix 2, table S18 (global prevalence and years lived with disability, 2019); the IHME GBD 2019 disability-weights table; Salomon JA et al., *Lancet Glob Health* 2015;3:e712–23, where the weights were estimated.

## Relationships

The demographic module supplies the canonical population, background mortality and migration. The annual coordinator derives the asthma population at risk from the canonical population and the current asthma state. `opening-state-reconciliation` creates one baseline opening state for both scenarios. Separate oral prednisolone, beclometasone and short-acting beta agonist repositories own the clinical intervention graph slices.

## Assumptions and limitations

The disease-free state is a local residual, not an additional population. The model is a marginal asthma estimate and must be reconciled to the canonical population. The live graph still contains legacy economic helper nodes that are outside the module contract and should move to metric modules when that separation is completed.

## Status

The disease graph, compiler contract, baseline template, and opening-state recipe are implemented. The source graph requires compiler lowering and is not a standalone national model.
