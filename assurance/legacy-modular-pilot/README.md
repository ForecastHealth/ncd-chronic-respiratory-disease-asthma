# Asthma Modular Pilot

This directory contains the first end-to-end modularisation pilot for the current asthma model.

The current goal is parity first. The component files split the monolithic asthma model into explicit composable units with contracts, and the composer rebuilds a runnable model that matches the original Rust output exactly for the asthma CR1 scenario. This is a controlled lowering step: the demographic component records the intended external boundary with the existing botech demographic model, while the current composed model still lowers that boundary to the embedded asthma demographic nodes so that parity can be proven before cross-model execution is introduced.

## Components

- `demographic-substrate`: population opening, births, ageing, migration, sex ratio, and background mortality as currently embedded in asthma.
- `asthma-epidemiology-core`: asthma state occupancy, prevalence allocation, incidence, remission, asthma mortality, and the incidence modifier hook.
- `tobacco-risk-factor`: tobacco prevalence, interventions, relative risk, PAF calculation, and the resolved asthma incidence modifier.
- `clinical-low-dose-beclom`: low-dose beclometasone coverage, disability effect, and mortality effect.
- `clinical-high-dose-beclom`: high-dose beclometasone coverage and disability effect.
- `clinical-oral-prednisolone`: oral prednisolone coverage and disability effect.
- `clinical-inhaled-short-acting-beta-agonist`: inhaled short-acting beta agonist coverage and disability effect.
- `burden-metrics`: healthy years lived, YLDs, YLLs, DALYs, and disability-weight transforms.
- `economic-metrics`: economic value calculation from healthy years lived, GDP per capita, and labour-force participation.
- `resource-handoffs`: population-reached and resource-population-reached surfaces for downstream resource or costing layers.

## Validation

The parity validation certificate compares the original asthma CR1 model run with the composed asthma CR1 model run using the same materialised scenario and the same unified API data bundle. The current validation passes when the Rust timestamped output CSV is byte-identical between the original and composed runs.

Generated materialised models, data bundles, and Rust result CSVs are discarded after hashing and comparison.
