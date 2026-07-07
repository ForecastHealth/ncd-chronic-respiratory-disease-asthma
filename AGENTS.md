# ncd-asthma

This repository is the asthma module for the modular botech NCD work. Treat the current source of truth as the module contract plus the module model, not the old monolithic scenario tooling.

## Current Source Of Truth

- `model.json` contains the asthma-owned botech graph. It owns asthma states and asthma intervention mechanics, including the asthma-local `DsFreeSus` state needed by the asthma calculation.
- `interface/asthma-epidemiology-core.module.contract.v1.json` declares what the module needs from the wider compiled model and what it publishes.
- `parameters/registry.v1.json` is the asthma parameter registry. Every editable asthma scenario parameter should be declared there and should point to the current model placement it controls.
- `parameters/templates/*.template.v1.json` are the asthma scenario templates. Templates should only set parameters from this module registry.
- `data/asthma-opening-balance-seed.recipe.v1.json` records the asthma opening-balance seeding contract used by the demography plus asthma proof compiler.

## Current Commands

Validate the module contract with:

```bash
python scripts/validate_module_contract.py
```

List the parameter registry with:

```bash
python scripts/orchestrator_scenarios.py catalog
```

List scenario templates with:

```bash
python scripts/orchestrator_scenarios.py templates
```

Materialize a template-applied asthma module model with:

```bash
python scripts/orchestrator_scenarios.py materialize --template-id asthma_cr1 --country ETH --start-year 2025 --end-year 2046 --output-dir /tmp/ncd-asthma-materialized
```

That materialized model is still a module model. The demography plus asthma proof compiler must lower demographic substrate inputs and asthma opening balances before it is a complete runnable proof model.

## Removed Legacy Shape

Do not recreate `scenarios/`, `build/`, `validation_suite/`, country-list folders, upload scripts, or JSONPath scenario application scripts unless Rory explicitly asks for a historical restore. Scenario ownership now belongs in `parameters/registry.v1.json` and `parameters/templates/`.
## CR3 intervention ownership

Appendix 3 CR3 intervention mechanics are not owned by this asthma disease module. The executable Botech graph slices for low-dose beclometasone, high-dose beclometasone, and inhaled short-acting beta agonist live in their own intervention repos under `/Users/rory/Models/`. This repo keeps the asthma disease states and shared transform landing nodes that those components connect to during compiler composition.

