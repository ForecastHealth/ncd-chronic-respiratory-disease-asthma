#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = Path("/Users/rory/Documents/botech-modular-structure/contracts")
STALE_TOKENS = ("build/", "scenarios/", "scenario-components")
JSON_PATH_RE = re.compile(r"\$\.(nodes|links)\[\?\(@\.id=='([^']+)'\)\]")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def ids_in_path(path: str) -> list[tuple[str, str]]:
    return [(kind, value) for kind, value in JSON_PATH_RE.findall(path)]


def strings_in(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(strings_in(item))
        return result
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(strings_in(item))
        return result
    return []


def validate() -> list[str]:
    errors: list[str] = []

    if (REPO_ROOT / "build").exists():
        fail(errors, "build/ still exists; asthma scenarios should be owned by parameters/templates")
    if (REPO_ROOT / "templates").exists():
        fail(errors, "top-level templates/ still exists; templates should live in parameters/templates")
    if (REPO_ROOT / "scripts" / "apply_scenario.py").exists():
        fail(errors, "scripts/apply_scenario.py still exists; materialisation should use the parameter registry directly")

    module_files = sorted((REPO_ROOT / "interface").glob("*.module.contract.v1.json"))
    if not module_files:
        fail(errors, "Missing interface/<module>.module.contract.v1.json")
        return errors
    module = load(module_files[0])
    module_id = module.get("module_id")
    repo_id = module.get("owner", {}).get("repo_id")
    if module.get("schema") != "botech.module-contract.v1":
        fail(errors, f"{module_files[0]} has wrong module contract schema")
    tests = module.get("validation", {}).get("internal_validity_tests", [])
    if "python scripts/validate_module_contract.py" not in tests:
        fail(errors, "Module contract validation command does not point at scripts/validate_module_contract.py")

    registry_path = REPO_ROOT / "parameters" / "registry.v1.json"
    if not registry_path.exists():
        fail(errors, "Missing parameters/registry.v1.json")
        return errors
    registry = load(registry_path)
    if registry.get("schema") != "botech.parameter-registry.v1":
        fail(errors, "parameters/registry.v1.json has wrong schema")
    if registry.get("module_id") != module_id:
        fail(errors, "Parameter registry module_id does not match module contract")
    if registry.get("owner", {}).get("repo_id") != repo_id:
        fail(errors, "Parameter registry owner repo_id does not match module contract")

    registry_ids = [item.get("parameter_id") for item in registry.get("parameters", [])]
    if len(registry_ids) != len(set(registry_ids)):
        fail(errors, "Parameter registry has duplicate parameter_id values")
    registry_set = set(registry_ids)

    for text in strings_in(registry):
        if any(token in text for token in STALE_TOKENS):
            fail(errors, f"Parameter registry still references removed scenario/build source: {text}")
            break

    model_path = REPO_ROOT / "model.json"
    if model_path.exists():
        model = load(model_path)
        node_ids = {node.get("id") for node in model.get("nodes", [])}
        link_ids = {link.get("id") for link in model.get("links", [])}
        for item in registry.get("parameters", []):
            for placement in item.get("placement_refs", []):
                if placement.get("kind") != "json_path":
                    fail(errors, f"Parameter {item.get('parameter_id')} has unsupported placement kind {placement.get('kind')}")
                    continue
                for kind, value in ids_in_path(placement.get("ref", "")):
                    if kind == "nodes" and value not in node_ids:
                        fail(errors, f"Parameter {item.get('parameter_id')} points to missing node {value}")
                    if kind == "links" and value not in link_ids:
                        fail(errors, f"Parameter {item.get('parameter_id')} points to missing link {value}")

    template_root = REPO_ROOT / "parameters" / "templates"
    template_files = sorted(template_root.glob("*.template.v1.json"))
    required_templates = {"asthma_baseline", "asthma_cr1", "asthma_cr3"}
    if not template_files:
        fail(errors, "Missing parameters/templates/*.template.v1.json")
    template_ids = set()
    forbidden_tokens = ("tobacco", "country", "start_year", "end_year", "runtime")
    for template_file in template_files:
        template = load(template_file)
        template_id = template.get("template_id")
        template_ids.add(template_id)
        if template.get("schema") != "botech.scenario-template.v1":
            fail(errors, f"{template_file} has wrong template schema")
        if template.get("module_id") != module_id:
            fail(errors, f"{template_file} module_id does not match registry")
        if template.get("owner", {}).get("repo_id") != repo_id:
            fail(errors, f"{template_file} owner repo_id does not match registry")
        if template.get("parameter_registry_ref") != "parameters/registry.v1.json":
            fail(errors, f"{template_file} does not point to parameters/registry.v1.json")
        for text in strings_in(template):
            if any(token in text for token in STALE_TOKENS):
                fail(errors, f"{template_file} still references removed scenario/build source: {text}")
                break
        for value in template.get("parameter_values", []):
            parameter_id = value.get("parameter_id")
            if parameter_id not in registry_set:
                fail(errors, f"{template_file} references unknown parameter_id {parameter_id}")
            if module_id == "asthma_epidemiology_core" and any(token in str(parameter_id) for token in forbidden_tokens):
                fail(errors, f"{template_file} contains non-asthma scenario parameter {parameter_id}")
    missing = required_templates - template_ids
    if missing:
        fail(errors, f"Missing required asthma templates: {sorted(missing)}")

    link_files = sorted((REPO_ROOT / "contracts" / "links").glob("*.link.contract.v1.json"))
    for link_file in link_files:
        link = load(link_file)
        if link.get("schema") != "botech.link-contract.v1":
            fail(errors, f"{link_file} has wrong link schema")
        source_repo = link.get("source", {}).get("repo_id")
        if source_repo and source_repo != repo_id:
            fail(errors, f"{link_file} is not source-owned by this repository")

    if module_id == "asthma_epidemiology_core":
        model = load(REPO_ROOT / "model.json")
        node_ids = {node.get("id") for node in model.get("nodes", [])}
        if "Births" in node_ids:
            fail(errors, "Asthma model.json still contains a standalone Births node")
        if "DsFreeSus" not in node_ids:
            fail(errors, "Asthma model.json is missing the asthma-local disease-free susceptible state DsFreeSus")
        stale_tobacco_nodes = {"BXOLckIN", "oGP2Nze1", "PjHF9FHh"} & node_ids
        if stale_tobacco_nodes:
            fail(errors, f"Asthma model.json still contains stale no-op tobacco/PIF nodes: {sorted(stale_tobacco_nodes)}")
        link_by_id = {link.get("id"): link for link in model.get("links", [])}
        background_link = link_by_id.get("kdE7JaZO", {})
        if background_link.get("generate_array"):
            fail(errors, "Asthma background mortality link still fetches demographic mortality directly instead of relying on compiler lowering")

    if not CONTRACT_ROOT.exists():
        fail(errors, "Cannot find botech-modular-structure contract root")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Module contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
