---
title: Asthma epidemiology
module_identifier: ncd-asthma
owner: Forecast Health
last_updated: 2026-07-19
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

## Relationships

The demographic module supplies the canonical population, background mortality and migration. The annual coordinator derives the asthma population at risk from the canonical population and the current asthma state. `opening-state-reconciliation` creates one baseline opening state for both scenarios. Separate oral prednisolone, beclometasone and short-acting beta agonist repositories own the clinical intervention graph slices.

## Assumptions and limitations

The disease-free state is a local residual, not an additional population. The model is a marginal asthma estimate and must be reconciled to the canonical population. The live graph still contains legacy economic helper nodes that are outside the module contract and should move to metric modules when that separation is completed.

## Status

The disease graph, compiler contract, baseline template, and opening-state recipe are implemented. The source graph requires compiler lowering and is not a standalone national model.
