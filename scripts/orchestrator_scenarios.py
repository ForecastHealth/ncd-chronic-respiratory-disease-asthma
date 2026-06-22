#!/usr/bin/env python3

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = REPO_ROOT / "build"
CONFIGS_ROOT = BUILD_ROOT / "configs"
COMPONENTS_ROOT = BUILD_ROOT / "components"
MODEL_PATH = REPO_ROOT / "model.json"
DEFAULT_TEMPLATE_ID = "asthma_baseline"
TEMPLATE_ALIASES = {
    "baseline": "asthma_baseline",
    "oral_prednisolone": "asthma_cr1",
    "cr1": "asthma_cr1",
    "cr3": "asthma_cr3",
}
TEMPLATE_KIND_OVERRIDES = {
    "asthma_baseline": "baseline",
    "asthma_cr1": "preset",
    "asthma_cr3": "preset",
    "asthma_null": "preset",
    "asthma_oral_prednisolone": "parameter_surface",
    "asthma_low_dose_beclom": "parameter_surface",
    "asthma_high_dose_beclom": "parameter_surface",
    "asthma_inhaled_beta_agonist": "parameter_surface",
}

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.apply_scenario import apply_scenario_to_model


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def merge_parameters(base_params: dict, new_params: dict) -> dict:
    result = copy.deepcopy(base_params)
    for key, value in new_params.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = {**result[key], **value}
        else:
            result[key] = copy.deepcopy(value)
    return result


def iter_template_configs() -> list[Path]:
    return sorted(CONFIGS_ROOT.rglob("*.yml"))


def template_id_for_config(path: Path) -> str:
    return path.relative_to(CONFIGS_ROOT).with_suffix("").as_posix()


def template_index() -> dict[str, Path]:
    return {template_id_for_config(path): path for path in iter_template_configs()}


def resolve_template_id(template_id: str) -> str:
    return TEMPLATE_ALIASES.get(template_id, template_id)


def template_kind(template_id: str) -> str:
    if template_id in TEMPLATE_KIND_OVERRIDES:
        return TEMPLATE_KIND_OVERRIDES[template_id]
    if template_id.startswith("who-bloomberg-investment-case/"):
        return "preset"
    return "custom"


def load_component_parameters(component_file: str) -> dict:
    component_path = COMPONENTS_ROOT / component_file
    if not component_path.exists():
        raise FileNotFoundError(f"Component file not found: {component_path}")
    return load_json(component_path)


def build_scenario_from_config_path(config_path: Path) -> tuple[dict, dict]:
    config = load_yaml(config_path)
    parameters = {}

    for component_file in config.get("components", []):
        parameters = merge_parameters(parameters, load_component_parameters(component_file))

    overrides = config.get("overrides", {})
    for param_name, override_value in overrides.items():
        if param_name not in parameters:
            parameters[param_name] = copy.deepcopy(override_value)
            continue
        if isinstance(override_value, dict):
            parameters[param_name] = {**parameters[param_name], **override_value}
        else:
            parameters[param_name]["value"] = override_value

    metadata = copy.deepcopy(config.get("metadata", {}))
    metadata.setdefault("date_created", datetime.now().strftime("%Y-%m-%d %H:%M"))
    return {"metadata": metadata, "parameters": parameters}, config


def ensure_runtime_parameters(scenario: dict) -> None:
    runtime_defaults = load_component_parameters("runtime.json")
    for param_name, param_value in runtime_defaults.items():
        scenario["parameters"].setdefault(param_name, copy.deepcopy(param_value))


def set_parameter_value(scenario: dict, param_name: str, value) -> None:
    if param_name not in scenario["parameters"]:
        raise KeyError(f"Unknown scenario parameter `{param_name}`")
    scenario["parameters"][param_name]["value"] = value


def parse_override(raw: str) -> tuple[str, object]:
    if "=" not in raw:
        raise ValueError(f"Override must use NAME=VALUE form: {raw}")
    name, raw_value = raw.split("=", 1)
    name = name.strip()
    raw_value = raw_value.strip()
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        value = raw_value
    return name, value


def visible_parameter_count(parameters: dict) -> int:
    return sum(1 for value in parameters.values() if not value.get("hidden"))


def build_catalog_payload() -> dict:
    templates = []
    config_lookup = template_index()
    default_config_path = config_lookup[DEFAULT_TEMPLATE_ID]
    default_scenario, _ = build_scenario_from_config_path(default_config_path)
    ensure_runtime_parameters(default_scenario)
    default_values = {
        name: payload.get("value")
        for name, payload in default_scenario["parameters"].items()
    }

    catalog_by_name: dict[str, dict] = {}
    for component_path in sorted(COMPONENTS_ROOT.glob("*.json")):
        component_name = component_path.name
        is_runtime_component = component_name == "runtime.json"
        component_payload = load_json(component_path)
        for param_name, param_payload in component_payload.items():
            entry = catalog_by_name.setdefault(
                param_name,
                {
                    "parameter_id": param_name,
                    "label": param_name,
                    "description": param_payload.get("description", ""),
                    "category": param_payload.get("category", "Other"),
                    "hidden": bool(param_payload.get("hidden")),
                    "paths": set(),
                    "default_value": default_values.get(param_name),
                    "source_components": set(),
                    "runtime_only": is_runtime_component,
                },
            )
            entry["paths"].update(param_payload.get("paths", []))
            entry["source_components"].add(component_name)
            entry["runtime_only"] = entry["runtime_only"] and is_runtime_component
            if not entry["description"] and param_payload.get("description"):
                entry["description"] = param_payload["description"]
            if entry["category"] == "Other" and param_payload.get("category"):
                entry["category"] = param_payload["category"]
            if param_name in default_values:
                entry["default_value"] = default_values[param_name]

    parameters = []
    for name in sorted(catalog_by_name):
        entry = catalog_by_name[name]
        parameters.append(
            {
                "parameter_id": entry["parameter_id"],
                "label": entry["label"],
                "description": entry["description"],
                "category": entry["category"],
                "hidden": entry["hidden"],
                "default_value": entry["default_value"],
                "paths": sorted(entry["paths"]),
                "source_components": sorted(entry["source_components"]),
                "runtime_only": entry["runtime_only"],
            }
        )

    return {
        "schema_version": "v1",
        "model_id": "ncd-asthma",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "parameters": parameters,
    }


def build_templates_payload() -> dict:
    templates = []
    for config_path in iter_template_configs():
        template_id = template_id_for_config(config_path)
        scenario, config = build_scenario_from_config_path(config_path)
        ensure_runtime_parameters(scenario)
        aliases = sorted(alias for alias, target in TEMPLATE_ALIASES.items() if target == template_id)
        templates.append(
            {
                "template_id": template_id,
                "template_kind": template_kind(template_id),
                "aliases": aliases,
                "label": config.get("metadata", {}).get("label", template_id),
                "description": config.get("metadata", {}).get("description", ""),
                "component_files": config.get("components", []),
                "override_parameter_names": sorted(config.get("overrides", {}).keys()),
                "parameter_count": len(scenario["parameters"]),
                "visible_parameter_count": visible_parameter_count(scenario["parameters"]),
                "config_ref": str(config_path),
            }
        )

    return {
        "schema_version": "v1",
        "model_id": "ncd-asthma",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "templates": templates,
    }


def materialize_template(
    *,
    template_id: str,
    scenario_id: str | None,
    country: str,
    start_year: int,
    end_year: int,
    output_dir: Path,
    overrides: list[str],
) -> dict:
    configs = template_index()
    resolved_template_id = resolve_template_id(template_id)
    if resolved_template_id not in configs:
        raise KeyError(f"Unknown template_id `{template_id}`")

    config_path = configs[resolved_template_id]
    scenario, config = build_scenario_from_config_path(config_path)
    ensure_runtime_parameters(scenario)

    set_parameter_value(scenario, "Country", country)
    set_parameter_value(scenario, "Start Year", start_year)
    set_parameter_value(scenario, "End Year", end_year)

    applied_overrides = {}
    for raw_override in overrides:
        name, value = parse_override(raw_override)
        set_parameter_value(scenario, name, value)
        applied_overrides[name] = value

    model = load_json(MODEL_PATH)
    materialized_model = apply_scenario_to_model(copy.deepcopy(model), scenario)

    output_dir.mkdir(parents=True, exist_ok=True)
    scenario_path = output_dir / "scenario.json"
    model_path = output_dir / "model.json"
    bundle_path = output_dir / "data_bundle.json"
    run_input_path = output_dir / "materialized.model-input.v1.json"

    write_json(scenario_path, scenario)
    write_json(model_path, materialized_model)

    materialized = {
        "metadata": {
            "artifact_version": "v1",
            "artifact_type": "standalone_botech_model",
            "name": f"ncd-asthma materialized run input: {scenario_id or template_id}",
        },
        "model_id": "ncd-asthma",
        "scenario_id": scenario_id or resolved_template_id,
        "template_id": resolved_template_id,
        "requested_template_id": template_id,
        "template_kind": template_kind(resolved_template_id),
        "materializer": {
            "repo_root": str(REPO_ROOT),
            "script": str(Path(__file__).resolve()),
        },
        "materialized_input": {
            "kind": "standalone_botech_model",
            "model_ref": str(model_path),
            "scenario_ref": str(scenario_path),
            "data_bundle_ref": str(bundle_path),
        },
        "resolved_values": {
            "country": country,
            "start_year": start_year,
            "end_year": end_year,
            "overrides": applied_overrides,
        },
        "provenance": {
            "source_model_ref": str(MODEL_PATH),
            "source_config_ref": str(config_path),
            "component_files": config.get("components", []),
        },
    }
    write_json(run_input_path, materialized)
    return {
        "status": "ok",
        "template_id": resolved_template_id,
        "requested_template_id": template_id,
        "scenario_id": scenario_id or resolved_template_id,
        "run_input": str(run_input_path),
        "model": str(model_path),
        "scenario": str(scenario_path),
        "data_bundle": str(bundle_path),
        "output_dir": str(output_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Expose orchestrator-facing template, catalog, and materialization helpers for ncd-asthma.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog_parser = subparsers.add_parser("catalog", help="Emit the parameter catalog.")
    catalog_parser.add_argument("--output", help="Optional output JSON path.")

    templates_parser = subparsers.add_parser("templates", help="Emit the template list.")
    templates_parser.add_argument("--output", help="Optional output JSON path.")

    materialize_parser = subparsers.add_parser("materialize", help="Materialize one named template into a runnable model.")
    materialize_parser.add_argument("--template-id", required=True, help="Template id from build/configs, for example asthma_baseline or asthma_cr1.")
    materialize_parser.add_argument("--scenario-id", default=None, help="Scenario id to record in the materialized artifact.")
    materialize_parser.add_argument("--country", default="AFG")
    materialize_parser.add_argument("--start-year", type=int, default=2025)
    materialize_parser.add_argument("--end-year", type=int, default=2050)
    materialize_parser.add_argument("--output-dir", required=True, help="Directory where scenario/model/materialized input should be written.")
    materialize_parser.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        help="Optional parameter override in NAME=JSON_VALUE form. Can be repeated.",
    )

    args = parser.parse_args()

    if args.command == "catalog":
        payload = build_catalog_payload()
        if args.output:
            write_json(Path(args.output).resolve(), payload)
        print(json.dumps(payload, indent=2))
        return

    if args.command == "templates":
        payload = build_templates_payload()
        if args.output:
            write_json(Path(args.output).resolve(), payload)
        print(json.dumps(payload, indent=2))
        return

    if args.command == "materialize":
        payload = materialize_template(
            template_id=args.template_id,
            scenario_id=args.scenario_id,
            country=args.country,
            start_year=args.start_year,
            end_year=args.end_year,
            output_dir=Path(args.output_dir).resolve(),
            overrides=args.overrides,
        )
        print(json.dumps(payload, indent=2))
        return

    raise ValueError(f"Unhandled command `{args.command}`")


if __name__ == "__main__":
    main()
