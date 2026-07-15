# NCD Asthma Module

This repository owns the asthma epidemiology graph. It models asthma as a marginal disease process over the one population supplied by the demographic module; its disease-free state is a derived residual within that process, not a second population.

The source module owns asthma incidence, prevalence, disability and mortality calculations. It exposes declared inputs for clinical treatment effects and tobacco-related incidence effects. The intervention calculations themselves live in separate intervention repositories, and shared population, mortality and health-metric calculations live outside this repository.

The compiler uses the module contract in `interface/` to reconcile the opening asthma states against the demographic population, bind selected intervention and risk-factor components, and supply annual background mortality. The plain source graph is therefore not a complete standalone national model.

The source parameter registry is in `parameters/registry.v1.json`. The source module exposes only its baseline template; comparison values are owned by selected intervention modules. Run `python scripts/validate_module_contract.py` to check the source graph and contract before syncing a release.
