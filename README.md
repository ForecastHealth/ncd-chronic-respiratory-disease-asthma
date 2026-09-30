---
title: Asthma epidemiology
module_identifier: ncd-asthma
owner: Forecast Health
last_updated: 2026-09-29
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

## Inputs and outputs

Required inputs are the canonical opening population, reconciled asthma opening prevalence and background mortality rates. Optional inputs are net migration rates, an incidence modifier, clinical disability effects and clinical mortality effects. The module publishes the asthma episode population, asthma incidence flow and asthma-specific mortality flow as age-sex arrays.

## Parameters and templates

The source module exposes only `asthma_baseline`. The disease parameter registry is empty because comparison values belong to selected intervention modules. The compiler assembles Appendix 3 CR1 and CR3 from their separate intervention repositories.

## Data and evidence

[`model.json`](model.json) is the executable disease graph. The [module contract](interface/asthma-epidemiology-core.module.contract.v1.json) defines composition and runtime semantics. The [opening-state recipe](data/asthma-opening-balance-seed.recipe.v1.json) defines baseline initialization. The contract identifies Spectrum/OneHealth asthma material and the current method-fix reference as default provenance.

The CR1 resource block in [`resource_requirements.json`](resource_requirements.json) uses the same US dollar unit prices as `ncd-asthma-asthmaoralprednisolone`: ipratropium 20 mcg is 0.022 per puff and prednisolone is 0.2628 per tablet, from the OneHealth Tool drug and supply price list. The earlier values, 0.09 and 1.13, were Malaysian ringgit prices from the UNDP costing workbook.

Staff time is priced from one shared salary item per staff type, `cost-item.workforce-salary.<type>`: `nurse`, `generalist-primary-care-doctor`, `specialist`, `therapist` and `counsellor`. A type is the same item in every module that uses it, so a generalist minute costs the same everywhere, and each type can be edited on its own: a specialist can be paid differently from a generalist doctor. The item is an annual salary. Its default is the country's WHO-CHOICE annual salary from the data service for the type's cadre (skill level 4 for doctors and specialists, 3 for nurses and therapists, 2 for counsellors); the cadre is the default source, not the item. A staff minute costs that salary divided by 126,720 working minutes a year (8 hours, 22 days a month, 12 months). The data service uses this convention for its WHO-CHOICE cost per minute, and every clinical staff cost has used it. The per-minute values in the resource graphs are defaults for use without a country. Tobacco policy programme roles are separate staff types, since none is the same job as a clinical one.

## Relationships

The demographic module supplies the canonical population, background mortality and migration. The annual coordinator derives the asthma population at risk from the canonical population and the current asthma state. `opening-state-reconciliation` creates one baseline opening state for both scenarios. Separate oral prednisolone, beclometasone and short-acting beta agonist repositories own the clinical intervention graph slices.

## Assumptions and limitations

The disease-free state is a local residual, not an additional population. The model is a marginal asthma estimate and must be reconciled to the canonical population. The live graph still contains legacy economic helper nodes that are outside the module contract and should move to metric modules when that separation is completed.

## Status

The disease graph, compiler contract, baseline template, and opening-state recipe are implemented. The source graph requires compiler lowering and is not a standalone national model.
